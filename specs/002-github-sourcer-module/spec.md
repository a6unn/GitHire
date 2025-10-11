# Feature Specification: GitHub Sourcer Module

**Feature Branch**: `002-github-sourcer-module`
**Created**: 2025-10-05
**Status**: Clarified
**Input**: User description: "GitHub Sourcer module that accepts JobRequirement JSON from JD Parser and searches GitHub API for matching developers based on skills, experience level, and location, returning candidate profiles with repositories, languages, and activity metadata"

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts ✓
   → Input: JobRequirement (from Module 001)
   → Action: Search GitHub for developers
   → Output: Candidate profiles with metadata
   → Constraints: GitHub API limits, public data only
3. Mark unclear aspects ✓
   → See [NEEDS CLARIFICATION] markers below
4. Fill User Scenarios & Testing ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
   → WARN: Some clarifications needed
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

The GitHub Sourcer receives structured job requirements (from the JD Parser) and needs to find matching software developers on GitHub. It should:
1. **Search** GitHub for users whose public profiles match the required skills
2. **Filter** results based on programming languages, location, and activity level
3. **Retrieve** detailed profile information including bio, repositories, and contribution activity
4. **Return** a list of candidate profiles ready for ranking

The module operates as part of the recruitment pipeline and doesn't interact directly with end users.

### Acceptance Scenarios

1. **Given** a JobRequirement with skills=["Python", "FastAPI"], **When** the sourcer searches GitHub, **Then** it returns developers who have Python and FastAPI in their public repositories

2. **Given** a JobRequirement with location_preferences=["Tamil Nadu"], **When** the sourcer searches GitHub, **Then** it prioritizes developers with "Tamil Nadu" or nearby locations in their profiles

3. **Given** a JobRequirement with years_of_experience={min: 5}, **When** the sourcer searches GitHub, **Then** it uses account age and repository maturity as proxies for experience level

4. **Given** a JobRequirement with required_skills=["JavaScript", "React"], **When** searching GitHub, **Then** candidate profiles include their top repositories that use these technologies

5. **Given** 1000 potential matches on GitHub, **When** the sourcer processes results, **Then** it returns top 25 candidates based on skill match strength

6. **Given** a search in progress, **When** GitHub API rate limit is reached, **Then** the sourcer returns partial results with a warning about incomplete data

7. **Given** a JobRequirement requesting "Senior" seniority, **When** sourcing candidates, **Then** profiles include metrics like account age, stars received, and contribution frequency to infer seniority

8. **Given** repeated searches for similar roles, **When** the sourcer runs, **Then** it uses cached GitHub data (if recent) to avoid redundant API calls

#### Enhanced Location Matching Scenarios

9. **Given** a JobRequirement with location="Chennai", **When** the sourcer searches GitHub, **Then** it matches candidates with "Chennai" (1.0 score), "Tamil Nadu" (0.7 score), and "India" (0.3 score) in descending priority

10. **Given** a candidate profile with location="Bangalore, Karnataka, India", **When** JobRequirement specifies location="Karnataka", **Then** the candidate receives a state-level match with 0.7 confidence

11. **Given** a candidate profile with location="Bangalor" (typo), **When** JobRequirement specifies location="Bangalore", **Then** the fuzzy matching identifies the candidate with appropriate confidence reduction

#### Library-Level Skills Detection Scenarios

12. **Given** a JobRequirement with required_skills=["pandas", "numpy"], **When** searching for candidates, **Then** profiles include developers who use these specific libraries, not just Python in general

13. **Given** a candidate with repositories containing pandas in dependencies, **When** analyzing skills, **Then** the candidate receives high confidence score (0.8+) for pandas skill

14. **Given** a candidate whose repositories have topics=["pandas", "numpy"], **When** analyzing skills, **Then** the repository topics contribute to skill confidence scoring

15. **Given** a candidate whose bio mentions "data science with pandas", **When** analyzing skills, **Then** the bio text contributes to pandas skill detection

16. **Given** primary skill detection method fails, **When** analyzing candidate skills, **Then** the module uses fallback signals (topics, languages, bio) to calculate confidence scores

#### Performance and Batching Scenarios

17. **Given** 5,000 candidate profiles to enrich, **When** the sourcer processes them, **Then** it uses batched API requests (10-50 profiles per request) instead of sequential calls

18. **Given** batched API requests, **When** processing 5,000 candidates, **Then** the module completes within 3-5 minutes

18a. **Given** 30 candidate profiles to enrich with skill detection, **When** the sourcer processes them in parallel, **Then** all candidates are processed concurrently within 30-60 seconds (vs 18+ minutes sequential)

18b. **Given** a candidate with 100 repositories, **When** analyzing their skills, **Then** the module analyzes only the top 15 most-starred repositories to optimize performance while maintaining 90%+ accuracy

18c. **Given** Redis cache is unavailable, **When** enriching candidates, **Then** the module uses in-memory cache fallback to ensure candidate data persists between enrichment and ranking phases

#### Progressive Location Search Quality Scenarios

24. **Given** a JobRequirement with location="Chennai, Tamil Nadu, India", **When** the sourcer constructs the search query, **Then** it uses "location:chennai" (city-level) first, not "location:india" (country-level)

25. **Given** a city-level search returns 5 results (< 10 threshold), **When** the sourcer evaluates results, **Then** it automatically broadens to state-level search ("location:tamil nadu")

26. **Given** a state-level search returns 8 results (< 10 threshold), **When** the sourcer evaluates results, **Then** it automatically broadens to country-level search ("location:india")

27. **Given** any location search, **When** the sourcer constructs the GitHub query, **Then** it includes "type:user" to exclude organizations from results

28. **Given** a search query constructed, **When** executing the GitHub API search, **Then** the query does not include "sort:followers" to use GitHub's default relevance sorting instead

29. **Given** candidates ranked by ensemble scoring, **When** filtering by minimum score, **Then** the threshold is 0.2 (not 0.3) to allow more candidates while maintaining quality

#### Skill Confidence Scoring Scenarios

19. **Given** a candidate with multiple skill indicators, **When** calculating skill confidence, **Then** the module combines repository dependencies (primary), topics, languages, bio, and starred repos with appropriate weights

20. **Given** a candidate with skill confidence score 0.85, **When** returning results, **Then** the output includes the confidence score and indicates which signals contributed to it

#### Advanced Discovery Scenarios (Optional - BigQuery)

21. **Given** BigQuery is configured, **When** searching for Python developers with 20+ merged PRs, **Then** the module queries GHArchive dataset first, then enriches via GitHub API

22. **Given** BigQuery query returns 5,000 usernames, **When** enriching profiles, **Then** the module uses GraphQL batching to fetch all profiles within 3-5 minutes

23. **Given** BigQuery is not configured or fails, **When** searching for candidates, **Then** the module falls back to GitHub Search API without errors

### Edge Cases

- What happens when required skills are not found in any GitHub profiles?
  - Return empty result set with message: "No candidates found matching criteria"

- What happens when a candidate's profile is incomplete (missing bio, location, or repos)?
  - Include the candidate but mark missing fields as null/empty

- What happens when GitHub API is down or unreachable?
  - Return error indicating service unavailable, suggest retry

- What happens when searching for very common skills (e.g., "JavaScript" returns millions)?
  - Apply additional filters (location, activity level, stars) to narrow results

- What happens when a JobRequirement has conflicting criteria (e.g., Junior with 10+ years)?
  - Process all criteria as-is; ranking module will handle contradictions

- What happens when location is specified as "remote"?
  - Search globally without location filter

- What happens when a location string cannot be parsed into city/state/country?
  - Perform text-based matching on the original location string and assign low confidence score (0.3)

- What happens when primary skill detection method (dependencies) fails or is unavailable?
  - Use fallback ensemble scoring combining topics (35%), languages (25%), repo names (15%), bio/starred (25%)

- What happens when a candidate has repositories without topics?
  - Rely on other signals (languages, bio, repo names) for skill detection; topics signal weight is redistributed

- What happens when a library name is ambiguous (e.g., "React" could be React.js or React Native)?
  - Treat as the same skill; ranking module can differentiate based on repository descriptions

- What happens when batch API requests partially fail?
  - Return successfully enriched candidates and log failures; include partial results warning in metadata

- What happens when a candidate's location has typos (e.g., "Bangalor" instead of "Bangalore")?
  - Use fuzzy matching with Levenshtein distance to identify likely matches with reduced confidence

- What happens when BigQuery is configured but returns an error?
  - Log the error, fall back to GitHub Search API, and continue normally

- What happens when BigQuery query costs exceed budget?
  - Cache results aggressively (24 hours for same query), use query limits, alert user of cost concerns

---

## Requirements *(mandatory)*

### Functional Requirements

#### Input Processing
- **FR-001**: Module MUST accept JobRequirement JSON as input (output from Module 001)
- **FR-002**: Module MUST extract search criteria from JobRequirement: required_skills, preferred_skills, location_preferences, seniority_level, years_of_experience
- **FR-003**: Module MUST validate that JobRequirement contains at least one required_skill before searching

#### GitHub Search
- **FR-004**: Module MUST search GitHub for users whose public profiles match required skills
- **FR-005**: Module MUST query based on programming languages used in public repositories
- **FR-006**: Module MUST filter by location if location_preferences are specified in JobRequirement
- **FR-007**: Module MUST prioritize developers with active contributions (recent commits, PRs, issues)
- **FR-008**: Module MUST return top 25 matching candidates

#### Advanced Discovery (Optional - GHArchive/BigQuery)
- **FR-042**: Module MAY use GHArchive BigQuery dataset for initial candidate discovery when configured
- **FR-043**: Module SHOULD query BigQuery for activity-based filtering (e.g., users with 20+ merged PRs in specific language)
- **FR-044**: Module MUST fall back to GitHub Search API if BigQuery is unavailable or not configured
- **FR-045**: Module SHOULD cache BigQuery results to minimize query costs ($0.50-$1 per query)

#### Enhanced Location Filtering
- **FR-024**: Module MUST parse location strings into hierarchical components (city, state, country)
- **FR-025**: Module MUST match candidates using priority scoring: exact city match (1.0), state match (0.7), country match (0.3)
- **FR-026**: Module SHOULD handle location variants (e.g., "Chennai" matches "Chennai, Tamil Nadu, India")
- **FR-027**: Module MUST use fuzzy matching to handle typos in location strings

#### Progressive Location Search Quality
- **FR-046**: Module MUST search GitHub using the most specific location available (city > state > country)
- **FR-047**: Module MUST implement progressive location broadening when initial results are insufficient (< 10 candidates)
- **FR-048**: Module MUST exclude organizations from search results using GitHub's type filter
- **FR-049**: Module MUST use GitHub's default relevance sorting instead of follower-based sorting
- **FR-050**: Module MUST lower minimum score threshold to 0.2 (from 0.3) to increase candidate yield while maintaining quality

#### Library-Level Skills Detection
- **FR-028**: Module MUST detect specific library usage beyond programming languages (e.g., pandas, numpy for Python; React, Express for JavaScript)
- **FR-029**: Module MUST analyze repository dependencies to identify library-level skills
- **FR-030**: Module MUST combine multiple signals for skill confidence scoring: repository topics, languages, bio, starred repositories
- **FR-031**: Module MUST assign confidence scores to each detected skill (0.0 to 1.0)
- **FR-032**: Module MUST support fallback detection methods when primary signals are unavailable

#### Multi-Signal Skill Analysis
- **FR-033**: Module SHOULD analyze repository topics as a skill detection signal
- **FR-034**: Module SHOULD analyze repository names for skill keywords
  - **IMPLEMENTED** (2025-10-09): Repository Name Analysis
  - **Validation Results**: Tested with 10 real Chennai Python developers
    - **Coverage**: 60% (6/10 candidates have framework repos)
    - **Repos Found**: 47 framework-related repos across 855 total repos
    - **Breakdown**: Django (23 repos), Flask (14 repos), FastAPI (9 repos)
    - **Signal Strength**: Avg 7.8 framework repos per matching candidate
  - **Signal Weight**: 0.60 (medium-high confidence)
  - **Boost Factor**: +20% per repository with skill keyword in name/description
  - **Examples**: `django-blog`, `celery-fastapi-starter-pack`, `flask-tutorial` correctly detect Django, FastAPI, Flask
  - **Impact**: 15-20% confidence boost for candidates with framework-named repos
- **FR-035**: Module SHOULD analyze user bio and starred repositories for skill indicators
- **FR-036**: Module MUST calculate ensemble skill scores by combining multiple signals with appropriate weights

#### Data Retrieval
- **FR-009**: Module MUST retrieve candidate profile data: GitHub username, name, bio, location, public email (if available)
- **FR-010**: Module MUST retrieve repository data: top repositories, languages used, stars/forks count
- **FR-011**: Module MUST retrieve activity data: total contributions, account creation date, recent activity indicators
- **FR-012**: Module MUST only access public GitHub data (no authentication required for candidate profiles)

#### Performance & Caching
- **FR-013**: Module MUST complete search within flexible allocation from the overall 2-minute pipeline budget (no hard module-specific limit)
- **FR-014**: Module MUST cache GitHub API responses for 1 hour to avoid redundant calls for same search criteria
- **FR-014b**: Module MUST use in-memory cache fallback when Redis is unavailable to ensure candidate data persists during processing
- **FR-015**: Module MUST respect GitHub API rate limits (5000 req/hour for authenticated, 60 req/hour for unauthenticated)
- **FR-016**: Module MUST stop searching and return partial results if rate limit is reached
- **FR-037**: Module MUST use batched API requests to fetch multiple candidate profiles efficiently
- **FR-037b**: Module MUST process candidates in parallel using async/await concurrency patterns
- **FR-037c**: Module MUST limit repository analysis to top N starred repos per candidate (default: 15) to optimize processing time
- **FR-038**: Module SHOULD complete profile enrichment for 30 candidates within 30-60 seconds (optimized from 18+ minutes)

#### Output Format
- **FR-017**: Module MUST return list of Candidate objects with standardized structure
- **FR-018**: Each Candidate MUST include: github_username, name, bio, location, top_repos (list), languages (list), contribution_count, account_age_days
- **FR-019**: Module MUST return empty list (not error) if no candidates match criteria
- **FR-020**: Module MUST return metadata with results: total_found, returned_count, search_timestamp, rate_limit_remaining
- **FR-039**: Each Candidate MUST include skill confidence scores for matched skills
- **FR-040**: Each Candidate MUST include parsed location components (city, state, country) if location is available
- **FR-041**: Module MUST include data source information showing which signals contributed to skill detection

#### Error Handling
- **FR-021**: Module MUST return error if GitHub API is unreachable
- **FR-022**: Module MUST return partial results if some profiles fail to load (with warning)
- **FR-023**: Module MUST log all API errors for debugging

### Key Entities

#### Candidate (Output)
- Represents a GitHub developer profile
- Attributes:
  - github_username (unique identifier)
  - name (display name)
  - bio (profile description)
  - location (geographic location from profile)
  - location_parsed (structured location: city, state, country, confidence)
  - public_email (if available, else null)
  - top_repos (list of repository objects: name, description, stars, languages)
  - languages (list of programming languages used, e.g., ["Python", "JavaScript"])
  - skill_confidence_scores (map of skill → confidence score 0.0-1.0)
  - skill_signals (map of skill → list of detection sources: dependencies, topics, bio, etc.)
  - contribution_count (total contributions in last year)
  - account_age_days (days since account creation)
  - profile_url (link to GitHub profile)
  - avatar_url (profile image)
  - fetched_at (timestamp when data was retrieved)
- Relationships: Generated from GitHub User API data, consumed by Module 003 (Ranking Engine)

#### SearchCriteria (Internal)
- Represents processed search parameters from JobRequirement
- Attributes:
  - required_languages (extracted from required_skills)
  - preferred_languages (extracted from preferred_skills)
  - location_filter (from location_preferences)
  - min_account_age_days (estimated from years_of_experience)
  - activity_level (inferred from seniority_level: Junior=low, Senior=high)
- Relationships: Derived from JobRequirement (Module 001 output)

#### SearchResult (Output Metadata)
- Represents search execution metadata
- Attributes:
  - total_candidates_found (total matches on GitHub)
  - candidates_returned (number in response, limited by FR-008)
  - search_timestamp (when search executed)
  - rate_limit_remaining (GitHub API quota left)
  - cache_hit (boolean, whether results came from cache)
  - execution_time_ms (how long search took)
  - batching_used (boolean, whether batched API requests were used)
  - skill_detection_method (primary or fallback)
  - location_match_distribution (count of city/state/country matches)
- Relationships: Returned alongside Candidate list

#### LocationHierarchy (New)
- Represents parsed location components
- Attributes:
  - original_text (raw location string from profile)
  - city (extracted city name, null if not found)
  - state (extracted state/region name, null if not found)
  - country (extracted country name, null if not found)
  - match_confidence (how confident the parser is: 0.0-1.0)
  - match_level (which level matched: "city", "state", or "country")
- Relationships: Embedded in Candidate entity
- User Value: Enables hierarchical location matching (Chennai → Tamil Nadu → India)

#### SkillConfidence (New)
- Represents skill detection confidence
- Attributes:
  - skill_name (e.g., "pandas", "React")
  - confidence_score (0.0 to 1.0)
  - detection_signals (list of sources: ["dependencies", "topics", "bio"])
  - signal_weights (map showing contribution of each signal)
  - is_primary_detection (boolean, true if detected via dependencies)
- Relationships: Embedded in Candidate entity
- User Value: Explains why a candidate was matched to a skill

---

## Dependencies

### Input Dependencies
- **Module 001 (JD Parser)**: Provides JobRequirement JSON as input
  - Required fields: required_skills (list), role (string or null)
  - Optional fields: preferred_skills, location_preferences, seniority_level, years_of_experience

### External Dependencies
- **GitHub API**: Public user search and profile data
  - Rate limits: 5000 req/hour (authenticated), 60 req/hour (unauthenticated)
  - Data accessed: user profiles, repositories, languages, contribution activity
  - Constraint: Public data only (privacy-first principle from constitution)

- **GHArchive BigQuery** (Optional): Historical GitHub event data for advanced discovery
  - Dataset: `githubarchive.year.*` (public dataset, free to query with BigQuery costs)
  - Query cost: ~$0.50-$1 per query (depends on data scanned)
  - Query time: 30-60 seconds for millions of events
  - Use case: Activity-based filtering (users with 20+ merged PRs, early framework adopters)
  - Fallback: GitHub Search API if BigQuery unavailable

### Output Consumers
- **Module 003 (Ranking Engine)**: Consumes Candidate list for scoring
- **Module 005 (Backend API)**: Persists Candidate data to database

---

## Performance Requirements

- **PR-001**: Search must complete within flexible allocation from 2-minute total pipeline budget
- **PR-002**: Module should return results even if GitHub API is slow (use timeouts and partial results)
- **PR-003**: 1-hour cache duration balances fresh data with API efficiency

---

## Constitutional Rules *(governance)*

### CR-001: No Hardcoded Configuration Values
**Rule**: All scoring weights, thresholds, timeouts, and matching parameters MUST be configurable via external configuration files or environment variables.

**Rationale**: Implementation details should be tunable without code changes to support A/B testing and optimization.

**Applies To**:
- Skill detection signal weights (dependencies, topics, languages, bio, repo names)
- Confidence score thresholds for skill matching
- Location matching confidence scores (city: 1.0, state: 0.7, country: 0.3)
- Fuzzy matching distance thresholds
- Batch sizes for API requests
- Cache TTL durations
- API rate limit thresholds
- Timeout values

**Examples**:
- ❌ BAD: `if skill_confidence > 0.7` (hardcoded threshold)
- ✅ GOOD: `if skill_confidence > config.skill_threshold` (configurable)
- ❌ BAD: `weights = {"dependencies": 0.5, "topics": 0.25}` (hardcoded weights)
- ✅ GOOD: `weights = config.get_skill_detection_weights()` (configurable)

### CR-002: No Hardcoded Location or Skill Aliases
**Rule**: All location name variants (e.g., "Bangalore" → "Bengaluru") and skill synonyms (e.g., "React.js" → "React") MUST be maintained in external data files.

**Rationale**: Location names and skill terminology evolve; hardcoding aliases creates maintenance burden and reduces flexibility.

**Applies To**:
- City name variants and aliases
- State/province name variations
- Country name variations
- Skill name synonyms and variations
- Technology name mappings (e.g., "JavaScript" ↔ "JS")

**Examples**:
- ❌ BAD: `if location in ["Bangalore", "Bengaluru", "Bengalooru"]` (hardcoded)
- ✅ GOOD: `if location in location_db.get_variants(city_id)` (data-driven)
- ❌ BAD: `skill_map = {"reactjs": "react", "react.js": "react"}` (hardcoded)
- ✅ GOOD: `skill_name = skill_db.normalize(skill_name)` (data-driven)

### CR-003: Ensemble Scoring Must Be Configurable
**Rule**: The multi-signal ensemble scoring algorithm MUST support dynamic weight adjustment and signal inclusion/exclusion without code changes.

**Rationale**: Optimal signal weights may vary by job type, seniority level, or over time as detection accuracy improves; configuration enables experimentation.

**Applies To**:
- Signal weight distribution (dependencies, topics, languages, bio, starred repos, repo names)
- Fallback strategy trigger conditions
- Minimum confidence thresholds per skill
- Signal availability handling (what to do when a signal is missing)

**Examples**:
- ❌ BAD: `score = deps*0.5 + topics*0.25 + lang*0.15 + bio*0.1` (hardcoded)
- ✅ GOOD: `score = ensemble.calculate(signals, weights=config.weights)` (configurable)

### CR-004: Transparency in Data Sources
**Rule**: Output MUST include metadata showing which data sources and signals contributed to each candidate match and confidence score.

**Rationale**: Users need to understand why candidates were selected; explainability builds trust and enables debugging.

**Applies To**:
- Skill confidence score explanations
- Location match level indicators
- Detection signal contributions
- Fallback method usage indicators

**Examples**:
- ✅ REQUIRED: Include `skill_signals` showing which sources detected each skill
- ✅ REQUIRED: Include `skill_detection_method` showing if primary or fallback was used
- ✅ REQUIRED: Include `location_parsed.match_level` showing city/state/country match

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted (input, action, output, constraints)
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated (23 functional requirements)
- [x] Entities identified (3 entities)
- [x] Review checklist passed

---

## Clarifications Resolved

1. **Result Count**: 25 candidates (moderate list, good for ranking)
2. **Search Time Limit**: Flexible allocation from overall 2-minute pipeline budget
3. **Cache Duration**: 1 hour (fresh data, higher API usage acceptable)

## Next Steps

1. **Plan implementation** → Create research, data model, contracts
2. **Generate tasks** → TDD task list
3. **Build module** → Following constitution principles
