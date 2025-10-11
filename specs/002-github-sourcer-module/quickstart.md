# Quickstart: GitHub Sourcer Module

**Module**: 002-github-sourcer-module
**Date**: 2025-10-06
**Purpose**: Manual test scenarios to validate GitHub Sourcer implementation

---

## Prerequisites

1. **GitHub Personal Access Token (PAT)**
   ```bash
   # Create token at: https://github.com/settings/tokens
   # Required scopes: public_repo (read-only access)
   export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
   ```

2. **Redis Server Running**
   ```bash
   # Start Redis locally
   redis-server
   # Or via Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Install Dependencies**
   ```bash
   pip install httpx redis pydantic pytest pytest-asyncio
   ```

---

## Scenario 1: Basic Search - Python Developers

**Input**: JobRequirement from Module 001 output

```json
{
  "role": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI"],
  "preferred_skills": ["Docker", "PostgreSQL"],
  "years_of_experience": {
    "min": 5,
    "max": null,
    "range_text": "5+ years"
  },
  "seniority_level": "Senior",
  "location_preferences": ["India"],
  "domain": null,
  "confidence_scores": {
    "role": {"score": 0.95, "source": "explicit"},
    "required_skills": {"score": 0.90, "source": "explicit"}
  },
  "original_input": "Looking for a Senior Python Developer with 5+ years experience...",
  "schema_version": "1.0.0"
}
```

**Expected Output**:
- `candidates`: List of 1-25 GitHub users
- Each candidate has:
  - `github_username` populated
  - `languages` includes "Python"
  - `account_age_days` >= 1825 (5 years * 365)
  - `top_repos` has at least 1 repo with Python
- `metadata.total_candidates_found` > 0
- `metadata.candidates_returned` <= 25
- `metadata.rate_limit_remaining` > 0

**Validation Steps**:
1. Run search with above input
2. Check first candidate has Python in languages
3. Verify candidate profile URL is accessible: `https://github.com/{username}`
4. Confirm at least 1 top repo uses Python

---

## Scenario 2: Location Filtering

**Input**: Tamil Nadu location preference

```json
{
  "role": "Frontend Developer",
  "required_skills": ["JavaScript", "React"],
  "preferred_skills": [],
  "years_of_experience": {"min": 2, "max": null, "range_text": "2+ years"},
  "seniority_level": "Mid-level",
  "location_preferences": ["Tamil Nadu", "Chennai"],
  "domain": null,
  "confidence_scores": {},
  "original_input": "Frontend dev in Tamil Nadu",
  "schema_version": "1.0.0"
}
```

**Expected Output**:
- Candidates have `location` field containing "India" or "Tamil Nadu" or "Chennai" (broadened to country)
- SearchCriteria internal query: `language:javascript location:india`

**Validation Steps**:
1. Check candidates have India-based locations (or null if not specified)
2. Verify GitHub query was constructed with location filter
3. Confirm metadata shows search was executed

---

## Scenario 3: Rate Limit Handling

**Input**: Trigger rate limit scenario (run 30+ searches rapidly)

**Setup**:
```python
# Disable cache temporarily
import os
os.environ["DISABLE_CACHE"] = "true"

# Run 35 searches in <1 minute
for i in range(35):
    search_github(job_requirement)
```

**Expected Behavior**:
- After 30 requests: rate limit warning appears
- Either:
  - A) Pauses until reset time, then continues
  - B) Returns partial results with warning in metadata
- `metadata.warnings` includes: `["Rate limit approaching, results may be incomplete"]`
- No crashes or exceptions

**Validation Steps**:
1. Monitor `X-RateLimit-Remaining` header in logs
2. Verify graceful degradation (partial results, not error)
3. Check metadata.warnings list

---

## Scenario 4: Cache Behavior

**Input**: Same JobRequirement run twice within 1 hour

**Test**:
```python
# First search (cache miss)
result1 = search_github(job_requirement)
assert result1["metadata"]["cache_hit"] == False

# Second search (cache hit)
result2 = search_github(job_requirement)
assert result2["metadata"]["cache_hit"] == True

# Results should be identical
assert result1["candidates"] == result2["candidates"]
```

**Expected Output**:
- First call: `cache_hit: false`, `execution_time_ms` > 1000
- Second call: `cache_hit: true`, `execution_time_ms` < 100
- Candidate data identical

**Validation Steps**:
1. Clear Redis: `redis-cli FLUSHDB`
2. Run first search, note execution time
3. Run second search immediately
4. Verify cache hit and faster execution

---

## Scenario 5: Empty/No Results

**Input**: Very specific criteria with no matches

```json
{
  "role": "Quantum Computing Engineer",
  "required_skills": ["Q#", "Quantum Annealing"],
  "preferred_skills": [],
  "years_of_experience": {"min": 10, "max": null, "range_text": "10+ years"},
  "seniority_level": "Principal",
  "location_preferences": ["Antarctica"],
  "domain": null,
  "confidence_scores": {},
  "original_input": "Quantum engineer in Antarctica",
  "schema_version": "1.0.0"
}
```

**Expected Output**:
```json
{
  "candidates": [],
  "metadata": {
    "total_candidates_found": 0,
    "candidates_returned": 0,
    "search_timestamp": "2025-10-06T10:00:00Z",
    "rate_limit_remaining": 4999,
    "cache_hit": false,
    "execution_time_ms": 1500,
    "warnings": ["No candidates found matching criteria"]
  }
}
```

**Validation Steps**:
1. Verify empty candidates list
2. Confirm metadata is still populated
3. Check warning message present

---

## Scenario 6: Profile Enrichment

**Input**: Search returns candidate "torvalds"

**Expected Candidate Object**:
```json
{
  "github_username": "torvalds",
  "name": "Linus Torvalds",
  "bio": "...",
  "location": "Portland, OR",
  "public_email": null,
  "top_repos": [
    {
      "name": "linux",
      "description": "Linux kernel source tree",
      "stars": 150000,
      "forks": 50000,
      "languages": ["C", "Assembly"],
      "url": "https://github.com/torvalds/linux"
    }
  ],
  "languages": ["C", "Assembly", "Shell"],
  "contribution_count": 2500,
  "account_age_days": 5000,
  "followers": 200000,
  "profile_url": "https://github.com/torvalds",
  "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
  "fetched_at": "2025-10-06T10:30:00Z"
}
```

**Validation Steps**:
1. Verify all required fields populated
2. Check `top_repos` sorted by stars (descending)
3. Confirm `languages` deduplicated and sorted
4. Validate URLs are accessible

---

## Scenario 7: Partial Profile Fetch Failures

**Setup**: Mock GitHub API to return 404 for some profiles

**Input**: Search returns 10 users, but 2 profiles fail to fetch

**Expected Behavior**:
- Successfully fetches 8 candidates
- Logs warnings for 2 failed profiles
- Returns 8 candidates (not error)
- Metadata shows `candidates_returned: 8`

**Validation Steps**:
1. Check logs contain: `"Failed to fetch profile for {username}: 404"`
2. Verify 8 candidates in output (not 10)
3. Confirm no exceptions raised

---

## Success Criteria

All 7 scenarios must pass for Phase 5 validation:

- [x] **Scenario 1**: Returns Python developers with correct skills
- [x] **Scenario 2**: Location filter applied correctly
- [x] **Scenario 3**: Rate limit handled gracefully
- [x] **Scenario 4**: Cache hit rate >50% for repeated queries
- [x] **Scenario 5**: Empty results handled without errors
- [x] **Scenario 6**: Profile data fully enriched
- [x] **Scenario 7**: Partial failures don't crash module

---

## Running All Scenarios

```bash
# Integration test suite
pytest tests/integration/test_github_search.py -v

# Manual CLI test
python -m src.github_sourcer.cli --input job_requirement.json

# Expected output
{
  "candidates": [...],
  "metadata": {
    "total_candidates_found": 247,
    "candidates_returned": 25,
    "cache_hit": false,
    "execution_time_ms": 3420,
    "warnings": []
  }
}
```

---

## Troubleshooting

**Issue**: `Authentication required` error
**Fix**: Set `GITHUB_TOKEN` environment variable

**Issue**: `Connection refused` to Redis
**Fix**: Start Redis server: `redis-server`

**Issue**: `Rate limit exceeded`
**Fix**: Wait 1 hour or use different GitHub token

**Issue**: Slow searches (>10 seconds)
**Fix**: Check Redis cache is working, verify network latency

---

**Next**: Generate tasks.md with /tasks command for implementation
