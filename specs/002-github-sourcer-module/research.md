# Research: GitHub Sourcer Module

**Date**: 2025-10-06
**Module**: 002-github-sourcer-module
**Purpose**: Research GitHub API, caching, and HTTP client decisions

---

## Research Question 1: GitHub Search API Capabilities

**Question**: Which GitHub API approach to use - REST `/search/users` vs GraphQL vs repository search?

**Research Findings**:
- **REST `/search/users`**:
  - Searches users by username, email domain, location
  - Query syntax: `language:python location:india`
  - Max 1000 results per query, returns 30 per page
  - Rate limit: 30 requests/minute for search endpoints

- **REST `/search/repositories`**:
  - Searches repos by language, stars, topics
  - Better for finding active contributors
  - Can extract owner info from repo results

- **GraphQL API**:
  - More flexible, fewer API calls
  - Can fetch user + repos + languages in one query
  - Same rate limits (5000 points/hour)
  - More complex to implement

**Decision**: **Use REST `/search/users` + individual profile fetches**

**Rationale**:
1. Simpler implementation (well-documented REST endpoints)
2. Direct user search with language/location filters
3. Two-step approach: search users, then fetch detailed profiles
4. Easier to cache (simple HTTP responses)
5. Proven pattern in similar tools

**Alternatives Considered**:
- GraphQL: More efficient but adds complexity for POC
- Repository search: Indirect (find repos, extract owners) - slower

---

## Research Question 2: GitHub Authentication

**Question**: Personal Access Token (PAT) vs GitHub App vs OAuth?

**Research Findings**:
- **Personal Access Token (PAT)**:
  - Simple: Just add to headers
  - Rate limit: 5000 req/hour (vs 60 unauthenticated)
  - User-scoped permissions
  - Best for POC/single-user tools

- **GitHub App**:
  - Higher rate limits (15000 req/hour)
  - Requires installation flow
  - Better for production multi-tenant apps

- **OAuth**:
  - For user-facing apps (login with GitHub)
  - Not needed for our use case (we search public data)

**Decision**: **Personal Access Token (PAT) with `public_repo` scope**

**Rationale**:
1. Simplest auth method for POC
2. 5000 req/hour sufficient for 100 concurrent users (per Module 000)
3. No installation/OAuth flow complexity
4. Easy to configure (env variable)
5. Public data only - minimal permissions needed

**Alternatives Considered**:
- GitHub App: Overkill for POC, implement if scaling later
- OAuth: Not needed (we don't act on behalf of users)

---

## Research Question 3: Rate Limiting Strategies

**Question**: How to handle GitHub API rate limits (30 search req/min, 5000 total/hour)?

**Research Findings**:
- GitHub returns `X-RateLimit-Remaining` header
- Search endpoint: 30 req/minute limit
- Core endpoints: 5000 req/hour limit
- 403 response when limit exceeded

**Decision**: **Proactive tracking + exponential backoff + partial results**

**Strategy**:
1. **Track quota**: Check `X-RateLimit-Remaining` header after each request
2. **Preemptive pause**: If <10 requests remaining, wait until reset
3. **Exponential backoff**: If 403 received, retry with 2^n second delays
4. **Partial results**: If rate limit hit mid-search, return candidates found so far
5. **Warning metadata**: Include `rate_limit_remaining` in SearchResult

**Rationale**:
- Prevents complete failures (partial results better than none)
- Respects GitHub ToS (no aggressive retry storms)
- Transparent to users (metadata shows rate limit status)

**Implementation**:
```python
class RateLimiter:
    def check_quota(self, response_headers):
        remaining = int(response_headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:
            reset_time = int(response_headers.get('X-RateLimit-Reset'))
            wait_seconds = reset_time - time.time()
            if wait_seconds > 0:
                logger.warning(f"Rate limit low, waiting {wait_seconds}s")
                time.sleep(wait_seconds)
```

---

## Research Question 4: Redis Caching Patterns

**Question**: How to structure Redis cache for 1-hour TTL (per clarification)?

**Research Findings**:
- Redis TTL: `SETEX key 3600 value` for 1-hour expiration
- Key structure options:
  - Hash of search criteria (deterministic)
  - Separate keys for search results vs profile data

**Decision**: **Two-tier caching with hashed keys**

**Cache Structure**:
```
# Search results cache (query → list of usernames)
Key: "search:{hash_of_criteria}"
Value: JSON list of usernames
TTL: 3600 seconds (1 hour)

# Profile cache (username → profile data)
Key: "profile:{username}"
Value: JSON of Candidate object
TTL: 3600 seconds (1 hour)

# Example:
search:abc123def -> ["user1", "user2", "user3"]
profile:user1 -> {full candidate JSON}
profile:user2 -> {full candidate JSON}
```

**Rationale**:
1. **Two-tier**: Reuse profiles across different searches
2. **Hashed keys**: Deterministic (same search = same key)
3. **Separate TTLs**: Can adjust profile cache independently
4. **Space efficient**: Profile stored once, referenced by multiple searches

**Hash Function**:
```python
def cache_key(job_req: JobRequirement) -> str:
    # Deterministic hash of search criteria
    criteria = {
        "skills": sorted(job_req.required_skills),
        "location": sorted(job_req.location_preferences),
        "seniority": job_req.seniority_level
    }
    hash_input = json.dumps(criteria, sort_keys=True)
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
```

**Alternatives Considered**:
- Single key per search: Wastes space (duplicate profiles)
- No hashing: Keys too long, hard to debug

---

## Research Question 5: Async HTTP Client

**Question**: httpx vs aiohttp for async GitHub API calls?

**Research Findings**:
- **httpx**:
  - Sync + async API (same interface)
  - Familiar requests-like API
  - Better timeout handling
  - Newer, well-maintained

- **aiohttp**:
  - Pure async (no sync fallback)
  - Slightly faster for high concurrency
  - More verbose API

**Decision**: **httpx for simplicity + sync/async flexibility**

**Rationale**:
1. Sync API useful for testing/debugging
2. Familiar requests-like interface (lower learning curve)
3. Built-in timeout handling (`httpx.Timeout(30.0)`)
4. POC doesn't need extreme concurrency (aiohttp's edge)
5. Better error messages for debugging

**Usage Pattern**:
```python
import httpx

async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(
        "https://api.github.com/search/users",
        params={"q": "language:python location:india"},
        headers={"Authorization": f"token {github_token}"}
    )
```

**Alternatives Considered**:
- aiohttp: Slightly faster but less ergonomic for POC
- requests: Sync-only, blocks on I/O

---

## Additional Decisions

### Skill → GitHub Query Translation

**Decision**: Map skills to GitHub `language:` filter

**Mapping Strategy**:
```python
SKILL_TO_GITHUB_LANGUAGE = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "react": "javascript",  # React uses JS
    "vue": "javascript",
    "angular": "typescript",
    "go": "go",
    "rust": "rust",
    "java": "java",
    # Frameworks map to base language
}
```

**Query Construction**:
```
required_skills = ["Python", "FastAPI"]
→ query = "language:python" (use most specific language)

location_preferences = ["Tamil Nadu", "Bangalore"]
→ query += " location:india" (broaden to country for API compatibility)
```

---

### Prioritization When >25 Results

**Decision**: GitHub's relevance sort + stars/followers as tiebreaker

**Strategy**:
1. Use GitHub's default relevance sort (best match first)
2. Fetch first 25 users from sorted results
3. If need tiebreaker: sort by `followers` desc (proxy for visibility)

**Rationale**:
- Trust GitHub's search relevance algorithm
- Don't over-engineer ranking (Module 003 handles that)
- Stars/followers indicate active, visible developers

---

### Partial Failure Handling

**Decision**: Continue on profile fetch errors, log and skip failed candidates

**Strategy**:
```python
candidates = []
for username in search_results:
    try:
        profile = await fetch_profile(username)
        candidates.append(profile)
    except Exception as e:
        logger.warning(f"Failed to fetch {username}: {e}")
        # Continue with other candidates

return candidates  # Partial results OK
```

**Rationale**:
- Partial results better than total failure
- Search may return some deleted/private accounts
- Logged warnings for debugging

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| HTTP Client | httpx | >=0.24.0 | Sync/async, requests-like API |
| Cache | redis-py | >=5.0.0 | Standard Redis client |
| Validation | pydantic | >=2.0.0 | Reuse from Module 001 |
| Testing | pytest + pytest-asyncio | >=7.4.0 | Async test support |

---

## Constitution Compliance Check

✅ **Privacy-First**: Only public GitHub API, no scraping
✅ **Single Source**: GitHub API only, no other integrations
✅ **Modular**: Clear input (JobRequirement) → output (Candidate list)
✅ **Transparent**: Returns metadata (rate limits, cache status)
✅ **No AI**: Pure API search (AI ranking happens in Module 003)

---

## Next Phase: Design & Contracts

With research complete, proceed to Phase 1:
1. Define data models (Candidate, SearchCriteria, SearchResult)
2. Create input/output JSON schemas
3. Write contract tests (TDD)
4. Design GitHub client interface
