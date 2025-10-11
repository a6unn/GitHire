# Tasks: GitHub Sourcer Module

**Input**: Design documents from `/specs/002-github-sourcer-module/`
**Prerequisites**: ✅ plan.md, ✅ research.md, ✅ data-model.md, ✅ contracts/

---

## Overview

**Module**: 002-github-sourcer-module (ENHANCED)
**Total Tasks**: 38 (expanded from 22, includes 3 optional BigQuery tasks)
**Estimated Duration**: 18-26 hours (was 8-12 hours)
**Approach**: TDD (Tests First, Implementation Second)

**Technology Stack**:
- Python 3.11+
- httpx (async HTTP client)
- redis-py 5.0+ (caching)
- pydantic v2 (validation)
- pytest + pytest-asyncio (testing)
- **NEW:** pyyaml (config management)
- **NEW:** python-Levenshtein (fuzzy matching)
- **NEW (OPTIONAL):** google-cloud-bigquery (GHArchive integration)

**Enhanced Features**:
- **GHArchive BigQuery discovery (optional)** - activity-based filtering
- Hierarchical location matching (city/state/country)
- Library-level skills detection (pandas, numpy, React)
- Multi-signal ensemble scoring
- GraphQL batching (4.6x speedup)
- Fallback detection strategy
- Configurable weights (no hardcoding)

---

## Phase 3.1: Setup (3 tasks)

- [ ] **T001** Create project structure for GitHub Sourcer module
  - Create: `src/github_sourcer/` directory
  - Create subdirectories: `models/`, `services/`, `lib/`
  - Create: `tests/contract/`, `tests/integration/`, `tests/unit/` for Module 002
  - Verify: Directory structure matches plan.md

- [ ] **T002** Add Module 002 dependencies to pyproject.toml
  - Add: `httpx >= 0.24.0` (async HTTP client)
  - Add: `redis >= 5.0.0` (caching)
  - Add: `pytest-asyncio >= 0.21.0` (async test support)
  - **NEW:** Add: `pyyaml >= 6.0` (config file parsing)
  - **NEW:** Add: `python-Levenshtein >= 0.21.0` (fuzzy string matching)
  - **NEW:** Add: `rapidfuzz >= 3.0.0` (faster fuzzy matching alternative)
  - Verify: `pip install -e .` succeeds
  - Run: `pytest --collect-only` to verify async support

- [ ] **T003** [P] Configure GitHub API authentication and Redis connection
  - Create: `src/github_sourcer/config.py` with environment variable loading
  - Add to `.env.example`: `GITHUB_TOKEN=ghp_...`, `REDIS_URL=redis://localhost:6379`
  - Validate: GitHub token has `public_repo` scope
  - Validate: Redis connection can be established
  - Document: Authentication setup in quickstart.md (already exists)

- [ ] **T003A** [NEW] [P] Create configuration files for ensemble scoring
  - Create: `src/config/skill_weights.yaml` with signal weights (dependencies: 0.5, topics: 0.25, etc.)
  - Create: `src/config/detection_config.yaml` with thresholds, batch sizes, timeouts
  - Create: `src/data/skill_aliases.json` with skill normalization mappings
  - Create: `src/data/location_aliases.json` with location variant mappings
  - Download: dr5hn/cities.json database to `src/data/cities.json` (151K cities)
  - Verify: All config files parse correctly (YAML/JSON validation)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (3 tasks)

- [ ] **T004** [P] Contract test for input schema in tests/contract/test_input_schema.py
  - Load: `specs/002-github-sourcer-module/contracts/input-schema.json`
  - Test: Valid JobRequirement passes schema validation
  - Test: Missing required_skills fails validation
  - Test: Invalid schema_version fails validation
  - Expected: All tests FAIL (models not imported yet)

- [ ] **T005** [P] Contract test for output schema in tests/contract/test_output_schema.py
  - Load: `specs/002-github-sourcer-module/contracts/output-schema.json`
  - Test: Valid Candidate object passes schema validation
  - Test: Valid SearchResult metadata passes schema validation
  - Test: candidates_returned > 25 fails validation
  - Test: Missing github_username fails validation
  - Expected: All tests FAIL (Candidate model doesn't exist)

- [ ] **T006** [P] Contract test for Candidate validation rules in tests/contract/test_candidate_validation.py
  - Test: contribution_count < 0 raises ValidationError
  - Test: account_age_days < 0 raises ValidationError
  - Test: top_repos > 5 truncates to 5
  - Test: languages are deduplicated and sorted
  - **NEW:** Test: skill_confidence_scores values between 0.0-1.0
  - **NEW:** Test: location_parsed has valid city/state/country or None
  - **NEW:** Test: skill_signals is non-empty when skill_confidence_scores present
  - Expected: All tests FAIL (Candidate model not implemented)

### Integration Tests (10 tasks - expanded from 5)

- [ ] **T007** [P] Integration test for GitHub user search in tests/integration/test_github_search.py
  - Mock: GitHub `/search/users` API response
  - Test: Search for "language:python location:india" returns users
  - Test: Empty search query raises ValueError
  - Test: Rate limit (403) triggers exponential backoff
  - Expected: All tests FAIL (GitHubClient not implemented)

- [ ] **T008** [P] Integration test for profile enrichment in tests/integration/test_profile_fetch.py
  - Mock: GitHub `/users/{username}` and `/users/{username}/repos` APIs
  - Test: Fetch profile for "torvalds" returns complete Candidate object
  - Test: Profile with no repos returns empty top_repos list
  - Test: Private profile (404) logs warning and skips candidate
  - Expected: All tests FAIL (profile fetching not implemented)

- [ ] **T009** [P] Integration test for caching behavior in tests/integration/test_cache_behavior.py
  - Test: First search sets cache (cache_hit=False)
  - Test: Second identical search reads cache (cache_hit=True, faster execution)
  - Test: Cache expires after 1 hour (TTL=3600)
  - Test: Different search criteria generate different cache keys
  - Expected: All tests FAIL (CacheService not implemented)

- [ ] **T010** [P] Integration test for end-to-end search in tests/integration/test_search_service.py
  - Test: JobRequirement → SearchService → List[Candidate] + SearchResult
  - Test: Required skills "Python" → candidates have Python in languages
  - Test: Location "Tamil Nadu" → SearchCriteria broadens to "india"
  - Test: Partial profile failures → return successful candidates only
  - Test: No results → empty candidates list with warning
  - Expected: All tests FAIL (SearchService not implemented)

- [ ] **T011** [P] Integration test for rate limiting in tests/integration/test_rate_limiting.py
  - Mock: X-RateLimit-Remaining header (simulate quota)
  - Test: Remaining < 10 → pauses until reset time
  - Test: 403 response → exponential backoff (2s, 4s, 8s)
  - Test: Rate limit hit mid-search → returns partial results with warning
  - Expected: All tests FAIL (RateLimiter not implemented)

- [ ] **T011A** [NEW] [P] Integration test for location parsing in tests/integration/test_location_parser.py
  - Test: "Chennai, Tamil Nadu, India" → city=Chennai, state=Tamil Nadu, country=India
  - Test: "Bangalore" → matches "Bengaluru" via aliases
  - Test: "Bangalor" (typo) → fuzzy matches "Bangalore" with reduced confidence
  - Test: Hierarchical matching: search="Chennai" matches city (1.0), state (0.7), country (0.3)
  - Expected: All tests FAIL (LocationParser not implemented)

- [ ] **T011B** [NEW] [P] Integration test for skill detection in tests/integration/test_skill_detector.py
  - Mock: GitHub Dependency Graph API response with pandas, numpy
  - Test: Primary detection (dependencies) → confidence 0.8-0.9
  - Test: Fallback detection (topics + languages + bio) → confidence 0.6-0.7
  - Test: Repository topics contribute to skill scoring
  - Test: Bio mentions "pandas" → contributes to skill confidence
  - Test: Skill normalization: "React.js" → "React"
  - Expected: All tests FAIL (SkillDetector not implemented)

- [ ] **T011C** [NEW] [P] Integration test for ensemble scoring in tests/integration/test_ensemble_scorer.py
  - Test: Load weights from config file (skill_weights.yaml)
  - Test: Combine multiple signals with weighted scoring
  - Test: Fallback weights when primary signal unavailable
  - Test: Confidence score capped at 1.0
  - Test: Skill detection method tracked (primary vs fallback)
  - Expected: All tests FAIL (EnsembleScorer not implemented)

- [ ] **T011D** [NEW] [P] Integration test for GraphQL batching in tests/integration/test_graphql_batching.py
  - Mock: GitHub GraphQL API batch query (10 users)
  - Test: Batch request fetches 10 user profiles in 1 API call
  - Test: Batch request faster than 10 sequential calls
  - Test: Partial batch failures handled gracefully
  - Test: metadata.batching_used = True when batching used
  - Expected: All tests FAIL (GraphQL batching not implemented)

- [ ] **T011E** [NEW] [P] Integration test for config loading in tests/integration/test_config_loader.py
  - Test: Load skill_weights.yaml with all required weights
  - Test: Load detection_config.yaml with thresholds, timeouts
  - Test: Load skill_aliases.json for skill normalization
  - Test: Load location_aliases.json for location variants
  - Test: Invalid config file → raises clear error
  - Expected: All tests FAIL (ConfigLoader not implemented)

- [ ] **T011F** [NEW] [OPTIONAL] [P] Integration test for BigQuery discovery in tests/integration/test_bigquery_client.py
  - Mock: BigQuery client response with usernames from GHArchive query
  - Test: Query for Python developers with 20+ merged PRs
  - Test: Query returns list of usernames within 60 seconds
  - Test: BigQuery error → gracefully falls back to GitHub Search API
  - Test: BigQuery disabled → skips BigQuery, uses GitHub Search directly
  - Expected: All tests FAIL (BigQueryClient not implemented)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (5 tasks - expanded from 3)

- [ ] **T012** [P] Create Candidate model in src/github_sourcer/models/candidate.py (ENHANCED)
  - Implement: Candidate Pydantic model per data-model.md
  - Implement: Repository nested model
  - **NEW:** Add: location_parsed (LocationHierarchy embedded model)
  - **NEW:** Add: skill_confidence_scores (dict[str, float] with 0.0-1.0 validation)
  - **NEW:** Add: skill_signals (dict[str, list[str]] showing detection sources)
  - Add validators: deduplicate languages, sort languages, truncate top_repos to 5
  - **NEW:** Add validator: skill_confidence_scores values between 0.0-1.0
  - Add: fetched_at defaults to datetime.utcnow()
  - Verify: tests/contract/test_candidate_validation.py passes

- [ ] **T013** [P] Create SearchResult model in src/github_sourcer/models/search_result.py (ENHANCED)
  - Implement: SearchResult Pydantic model per data-model.md
  - Add validators: candidates_returned <= 25
  - **NEW:** Add: batching_used (boolean)
  - **NEW:** Add: skill_detection_method (enum: "primary" or "fallback")
  - **NEW:** Add: location_match_distribution (dict with city/state/country counts)
  - Add: search_timestamp defaults to datetime.utcnow()
  - Verify: tests/contract/test_output_schema.py SearchResult tests pass

- [ ] **T014** [P] Create SearchCriteria model in src/github_sourcer/models/search_criteria.py
  - Implement: SearchCriteria Pydantic model per data-model.md
  - Implement: from_job_requirement() class method
  - Implement: _build_query(), _extract_country(), _map_seniority_to_activity()
  - Add: SKILL_TO_GITHUB_LANGUAGE mapping (reuse from Module 001)
  - Test: JobRequirement → SearchCriteria → query_string = "language:python location:india"

- [ ] **T014A** [NEW] [P] Create LocationHierarchy model in src/github_sourcer/models/location_hierarchy.py
  - Implement: LocationHierarchy Pydantic model per data-model.md
  - Fields: original_text, city, state, country, match_confidence, match_level
  - Add validator: match_confidence between 0.0-1.0
  - Add validator: match_level in ["city", "state", "country", null]
  - Verify: Embedded correctly in Candidate model

- [ ] **T014B** [NEW] [P] Create SkillConfidence model in src/github_sourcer/models/skill_confidence.py
  - Implement: SkillConfidence Pydantic model per data-model.md
  - Fields: skill_name, confidence_score, detection_signals, signal_weights, is_primary_detection
  - Add validator: confidence_score between 0.0-1.0
  - Add validator: detection_signals is non-empty list
  - Verify: Can serialize to JSON for API output

### Services & Libraries (12 tasks - expanded from 6)

- [ ] **T015** Create RateLimiter in src/github_sourcer/lib/rate_limiter.py
  - Implement: check_quota(response_headers) method
  - Logic: If X-RateLimit-Remaining < 10 → wait until X-RateLimit-Reset
  - Logic: On 403 → exponential backoff (2^n seconds, max 3 retries)
  - Add logging: Warn when rate limit low
  - Verify: tests/integration/test_rate_limiting.py passes

- [ ] **T016** Create GitHubClient in src/github_sourcer/services/github_client.py (ENHANCED)
  - Implement: async search_users(query: str) → list[str] (usernames)
  - Implement: async get_profile(username: str) → dict
  - Implement: async get_repos(username: str) → list[dict]
  - **NEW:** Implement: async batch_get_profiles_graphql(usernames: list[str]) → list[dict] (GraphQL batching)
  - **NEW:** Implement: async get_dependency_graph(username: str, repo: str) → dict (primary skill detection)
  - Use: httpx.AsyncClient with timeout=30.0
  - Add: Authorization header with GITHUB_TOKEN
  - Integrate: RateLimiter for quota tracking
  - Error handling: 404 → return None, 403 → trigger rate limiter, 502 → fallback detection
  - **NEW:** GraphQL batching: 10-50 users per query (configurable)
  - Verify: tests/integration/test_github_search.py, test_profile_fetch.py, test_graphql_batching.py pass

- [ ] **T017** Create CacheService in src/github_sourcer/services/cache_service.py
  - Implement: get_search_results(cache_key: str) → Optional[list[str]]
  - Implement: set_search_results(cache_key: str, usernames: list[str], ttl=3600)
  - Implement: get_profile(username: str) → Optional[Candidate]
  - Implement: set_profile(username: str, candidate: Candidate, ttl=3600)
  - Implement: _generate_cache_key(job_req: JobRequirement) → str (SHA256 hash)
  - Use: redis-py with TTL=3600 seconds
  - Verify: tests/integration/test_cache_behavior.py passes

- [ ] **T018** Implement profile enrichment in src/github_sourcer/services/profile_enricher.py
  - Implement: async enrich_profile(username: str, github_client: GitHubClient) → Candidate
  - Logic: Fetch user profile + repos, combine into Candidate object
  - Logic: Extract top 5 repos by stars
  - Logic: Aggregate languages from all repos (deduplicate, sort)
  - Logic: Calculate contribution_count from last year's activity
  - Logic: Calculate account_age_days from created_at
  - Error handling: 404 → raise ProfileNotFoundError
  - Verify: tests/integration/test_profile_fetch.py passes

- [ ] **T019** Create SearchService in src/github_sourcer/services/search_service.py
  - Implement: async search(job_req: JobRequirement) → dict (candidates + metadata)
  - Logic: Convert JobRequirement → SearchCriteria
  - Logic: Check cache first (CacheService.get_search_results)
  - Logic: If miss → GitHubClient.search_users() → get usernames
  - Logic: Enrich profiles (parallel async calls to ProfileEnricher)
  - Logic: Store in cache (CacheService.set_search_results + set_profile)
  - Logic: Return max 25 candidates + SearchResult metadata
  - Error handling: Partial profile failures → log and continue
  - Track: execution_time_ms, rate_limit_remaining, cache_hit
  - Verify: tests/integration/test_search_service.py passes

- [ ] **T016A** [NEW] Create LocationParser in src/github_sourcer/services/location_parser.py
  - Implement: parse_location(location_str: str) → LocationHierarchy
  - Logic: Split location string into city, state, country components
  - Integrate: Load cities.json database (151K cities)
  - Integrate: Load location_aliases.json for variant matching
  - Implement: hierarchical_match(search_location: str, candidate_location: LocationHierarchy) → (match_level, confidence)
  - Priority scoring: city=1.0, state=0.7, country=0.3
  - Verify: tests/integration/test_location_parser.py passes

- [ ] **T016B** [NEW] Create FuzzyMatcher in src/github_sourcer/lib/fuzzy_matcher.py
  - Implement: fuzzy_match(str1: str, str2: str, threshold: float) → (matched: bool, confidence: float)
  - Use: Levenshtein distance for typo detection
  - Load: Fuzzy matching threshold from detection_config.yaml
  - Logic: "Bangalor" matches "Bangalore" with confidence 0.8
  - Verify: Integrated with LocationParser for location matching

- [ ] **T016C** [NEW] Create SkillDetector in src/github_sourcer/services/skill_detector.py
  - Implement: async detect_skills(username: str, required_skills: list[str]) → dict[str, SkillConfidence]
  - Logic: Try primary detection via GitHubClient.get_dependency_graph()
  - Logic: On failure (502, timeout), use fallback ensemble
  - Integrate: Load skill_aliases.json for normalization
  - Implement: _detect_via_dependencies() (primary, 80-85% accuracy)
  - Implement: _detect_via_ensemble() (fallback, 70-75% accuracy)
  - Verify: tests/integration/test_skill_detector.py passes

- [ ] **T016D** [NEW] Create EnsembleScorer in src/github_sourcer/services/ensemble_scorer.py
  - Implement: calculate_skill_score(signals: dict, skill: str, weights: dict) → SkillConfidence
  - Integrate: Load weights from skill_weights.yaml (configurable)
  - Signals: repository topics, languages, bio, starred repos, repo names
  - Fallback weights: topics=0.35, languages=0.25, repo_names=0.15, bio_stars=0.25
  - Logic: Combine signals with weighted scoring, cap at 1.0
  - Track: Which signals contributed to score (transparency)
  - Verify: tests/integration/test_ensemble_scorer.py passes

- [ ] **T016E** [NEW] Create ConfigLoader in src/github_sourcer/lib/config_loader.py
  - Implement: load_skill_weights() → dict (from skill_weights.yaml)
  - Implement: load_detection_config() → dict (from detection_config.yaml)
  - Implement: load_skill_aliases() → dict (from skill_aliases.json)
  - Implement: load_location_aliases() → dict (from location_aliases.json)
  - Implement: load_cities_database() → list (from cities.json)
  - Error handling: Missing config file → raise ConfigurationError with clear message
  - Verify: tests/integration/test_config_loader.py passes

- [ ] **T016F** [NEW] [OPTIONAL] Create BigQueryClient in src/github_sourcer/services/bigquery_client.py
  - Implement: async query_active_users(language: str, min_prs: int, location: str) → list[str] (usernames)
  - SQL template: Query GHArchive for PullRequestEvent with filters
  - Integrate: Google Cloud BigQuery client library
  - Add: Query cost tracking and budget limits
  - Add: 24-hour caching for identical queries (minimize costs)
  - Error handling: BigQuery error → log and return None (triggers fallback)
  - Verify: tests/integration/test_bigquery_client.py passes

- [ ] **T019A** [NEW] [OPTIONAL] Enhance SearchService with BigQuery integration
  - Logic: If BigQuery configured → try BigQuery first, fallback to GitHub Search
  - Logic: If BigQuery returns usernames → enrich via GitHub API (GraphQL batching)
  - Logic: If BigQuery fails → fallback to GitHub Search API
  - Track: metadata.discovery_method = "bigquery" or "github_search"
  - Verify: Integration test with BigQuery enabled/disabled

- [ ] **T020** [P] Create CLI for GitHub Sourcer in src/github_sourcer/cli.py
  - Implement: `--input job_requirement.json` flag
  - Implement: `--output candidates.json` flag
  - Implement: `--pretty` for formatted JSON output
  - Read: JobRequirement JSON from file
  - Call: SearchService.search()
  - Write: Candidates + metadata to output file or stdout
  - Error handling: Invalid input file → clear error message
  - Verify: Manual test with `python -m src.github_sourcer.cli --input test.json`

---

## Phase 3.4: Integration (2 tasks)

- [ ] **T021** Wire all components together in src/github_sourcer/__init__.py
  - Export: Candidate, SearchResult, SearchCriteria, SearchService
  - Create: search_github(job_req: JobRequirement) convenience function
  - Initialize: Redis connection pool (global)
  - Initialize: httpx.AsyncClient (global)
  - Document: Module API in docstrings
  - Verify: `from src.github_sourcer import search_github` works

- [ ] **T022** Add logging and monitoring
  - Configure: logging to stdout with structured format
  - Log: Search query constructed, cache hit/miss, rate limit status
  - Log: Profile fetch failures (warning level)
  - Add: Execution time tracking for all GitHub API calls
  - Verify: Logs appear when running CLI

---

## Phase 3.5: Polish (NOT IMPLEMENTED YET - DEFERRED)

**Note**: These tasks are deferred until Phase 5 validation reveals issues.

- [ ] **T023** [P] Add unit tests for SearchCriteria logic in tests/unit/test_search_criteria.py
- [ ] **T024** [P] Add unit tests for cache key generation in tests/unit/test_cache_service.py
- [ ] **T025** [P] Performance test: Complete search in <5 seconds (tests/performance/)
- [ ] **T026** Run all 7 quickstart.md scenarios manually
- [ ] **T027** Update CLAUDE.md with Module 002 completion status

---

## Dependencies

**Sequential (Blocking)**:
- T001 → T002 → T003 (setup must complete first)
- T004-T011 (all tests) → T012-T020 (implementation)
- T012-T014 (models) → T016, T018, T019 (services depend on models)
- T015 (RateLimiter) → T016 (GitHubClient)
- T016, T017 (GitHubClient, CacheService) → T018, T019 (enricher, search service)
- T018 (ProfileEnricher) → T019 (SearchService)
- T019 (SearchService) → T020 (CLI)
- T012-T020 → T021 (integration)
- T021 → T022 (logging)

**Parallel (Can Run Together)**:
- T004, T005, T006 (contract tests - different files)
- T007, T008, T009, T010, T011 (integration tests - different files)
- T012, T013, T014 (models - different files)
- After T015 completes: T017 can run parallel to T016 (no dependency)

---

## Parallel Execution Examples

### Round 1: Contract Tests (After T003)
```bash
# Launch T004, T005, T006 in parallel
pytest tests/contract/test_input_schema.py &
pytest tests/contract/test_output_schema.py &
pytest tests/contract/test_candidate_validation.py &
wait
```

### Round 2: Integration Tests (After T006)
```bash
# Launch T007-T011 in parallel
pytest tests/integration/test_github_search.py &
pytest tests/integration/test_profile_fetch.py &
pytest tests/integration/test_cache_behavior.py &
pytest tests/integration/test_search_service.py &
pytest tests/integration/test_rate_limiting.py &
wait
```

### Round 3: Models (After T011)
```bash
# T012, T013, T014 can be implemented in parallel (different files)
```

---

## Validation Checklist

**GATE: Verify before marking Phase 3 complete**

- [x] All contracts have corresponding tests (T004, T005, T006)
- [x] All entities have model tasks (T012: Candidate, T013: SearchResult, T014: SearchCriteria)
- [x] All tests come before implementation (T004-T011 before T012-T020)
- [x] Parallel tasks are truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Tests written to FAIL before implementation (TDD enforced)

---

## Expected Test Results

**After T011 (All Tests Written)**:
- Total tests: ~30
- Passing: 0 (all should FAIL)
- Reason: Models and services not implemented yet

**After T020 (All Implementation Complete)**:
- Total tests: ~30
- Passing: 30 (100%)
- Reason: All contract and integration tests pass

**After T022 (Integration Complete)**:
- Manual validation with quickstart.md scenarios
- All 7 scenarios should pass

---

## Notes

- **TDD Discipline**: DO NOT implement before tests fail
- **Async First**: Use `async/await` for all I/O operations
- **Error Resilience**: Partial failures should not crash the module
- **Cache Hit Rate**: Target >50% for repeated searches
- **Rate Limit Respect**: Never exceed GitHub's 30 req/min search limit
- **Commit Frequency**: After each task completion

---

## Next Steps After Tasks Complete

1. Run full test suite: `pytest tests/ -v`
2. Validate with quickstart scenarios (manual testing)
3. Measure cache hit rate and execution time
4. Update plan.md with "Phase 4: Complete" status
5. Commit Module 002 and merge to main
6. Proceed to Module 003 (Ranking Engine)
