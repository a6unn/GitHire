# Implementation Plan: GitHub Sourcer Module

**Branch**: `002-github-sourcer-module` | **Date**: 2025-10-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-github-sourcer-module/spec.md`

## Summary
GitHub Sourcer module accepts JobRequirement JSON from JD Parser and searches GitHub API for matching developers based on skills, experience level, and location. Returns top 25 candidates with profile data, repositories, languages, and activity metrics.

**Enhanced Capabilities**:
- **GHArchive BigQuery Discovery (Optional)**: Query historical GitHub events for activity-based filtering (20+ merged PRs, early adopters) - $0.50-$1 per query, 30-60 second execution
- **Hierarchical Location Matching**: Parses locations into city/state/country hierarchy with priority scoring (Chennai → Tamil Nadu → India)
- **Library-Level Skills Detection**: Detects specific libraries (pandas, numpy, React) beyond programming languages using multi-signal ensemble
- **Multi-Signal Ensemble Scoring**: Combines repository dependencies, topics, languages, bio, starred repos, and repo names with configurable weights
- **GraphQL Batching**: Fetches 10-50 candidate profiles per API call for 4.6x performance improvement
- **Fallback Strategy**: Gracefully degrades from primary dependency detection (80-85% accuracy) to ensemble methods (70-75% accuracy)
- **Configurable Weights**: All scoring parameters, thresholds, and weights maintained in external config (no hardcoding)

Uses 1-hour caching to manage GitHub API rate limits (5000 req/hour authenticated).

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (async HTTP), pydantic v2 (validation), redis (caching)
**Storage**: Redis for 1-hour cache
**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux server / Docker container
**Project Type**: Single module (part of larger pipeline)
**Performance Goals**: Complete search within flexible allocation from 2-minute pipeline budget
**Constraints**: GitHub API rate limits (5000 req/hour authenticated), return max 25 candidates
**Scale/Scope**: Handle concurrent requests for 100 users, cache hit rate >50%

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development
- [x] No LLM required for this module (pure GitHub API search)
- [x] Module outputs to Ranking Engine which uses LLM for semantic skill matching

### II. Privacy-First Architecture
- [x] Only public GitHub API data used
- [x] No private repo or email scraping
- [x] No personal data stored (cache keys are search criteria hashes)
- [x] GDPR compliant (public data, short cache TTL)

### III. Single Source of Truth
- [x] GitHub REST/GraphQL API only
- [x] No LinkedIn/job board integration
- [x] GitHub API rate limits respected (5000 req/hour with auth token)
- [x] 1-hour caching strategy defined

### IV. Transparency & Explainability
- [x] Returns metadata: total_found, returned_count, rate_limit_remaining, cache_hit
- [x] Explains why candidates were selected (in Ranking Engine downstream)

### V. Modular Architecture
- [x] Standalone module with clear input/output interface
- [x] Input: JobRequirement JSON
- [x] Output: List[Candidate] + SearchResult metadata
- [x] Independently testable with mock GitHub API

**Constitution Status**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/002-github-sourcer-module/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (JSON schemas)
│   ├── input-schema.json
│   └── output-schema.json
└── tasks.md             # Phase 2 output (/tasks command)
```

### Source Code (repository root)
```
src/
├── models/
│   ├── job_requirement.py         # Reused from Module 001
│   ├── candidate.py                # ENHANCED: Candidate entity with skill_confidence, location_parsed
│   ├── search_result.py            # ENHANCED: SearchResult with batching_used, skill_detection_method
│   ├── location_hierarchy.py       # NEW: LocationHierarchy embedded model
│   └── skill_confidence.py         # NEW: SkillConfidence embedded model
├── services/
│   ├── github_client.py            # ENHANCED: GitHub REST + GraphQL batching
│   ├── bigquery_client.py          # NEW: GHArchive BigQuery integration (optional)
│   ├── search_service.py           # ENHANCED: Multi-signal ensemble orchestration + BigQuery fallback
│   ├── cache_service.py            # New: Redis caching layer
│   ├── location_parser.py          # NEW: Parse locations into city/state/country
│   ├── skill_detector.py           # NEW: Multi-signal skill detection
│   └── ensemble_scorer.py          # NEW: Configurable weight-based scoring
├── lib/
│   ├── rate_limiter.py             # New: Rate limit tracker
│   └── fuzzy_matcher.py            # NEW: Levenshtein distance for location typos
├── data/
│   ├── cities.json                 # NEW: dr5hn cities database (151K cities)
│   ├── skill_aliases.json          # NEW: Skill name normalization (React.js → React)
│   └── location_aliases.json       # NEW: Location variants (Bangalore → Bengaluru)
└── config/
    ├── skill_weights.yaml          # NEW: Ensemble scoring weights (configurable)
    └── detection_config.yaml       # NEW: Thresholds, batch sizes, timeouts

tests/
├── contract/
│   ├── test_input_schema.py   # Validate JobRequirement contract
│   └── test_output_schema.py  # Validate Candidate output contract
├── integration/
│   ├── test_github_search.py  # Test against real GitHub API (limited)
│   └── test_cache_behavior.py # Test caching logic
└── unit/
    ├── test_github_client.py  # Mock GitHub responses
    ├── test_search_service.py # Mock all dependencies
    └── test_rate_limiter.py   # Pure logic tests
```

**Structure Decision**: Single project structure with modular services. GitHub Sourcer is one module in the larger GitHire pipeline, sharing models with Module 001 (JD Parser).

## Phase 0: Outline & Research

**Research Tasks**:
1. GitHub Search API capabilities (user search vs code search vs repository search)
2. GitHub authentication methods (Personal Access Token vs GitHub App vs OAuth)
3. Rate limiting strategies (retry logic, backoff, quota tracking)
4. Redis caching patterns for API responses (TTL, key structure, invalidation)
5. Async HTTP client best practices (httpx vs aiohttp)
6. **NEW: GitHub GraphQL API batching** (fetch multiple users in single query)
7. **NEW: GitHub Dependency Graph API** (access repository dependencies for library detection)
8. **NEW: GHArchive BigQuery integration** (optional - historical event data, activity filtering)
9. **NEW: Location parsing libraries** (city/state/country extraction, fuzzy matching)
10. **NEW: Multi-signal ensemble scoring** (weight optimization, signal combination strategies)
11. **NEW: Configuration management** (YAML/JSON for weights, thresholds, aliases)

**Key Decisions to Make**:
- Which GitHub API endpoints to use (REST `/search/users` vs GraphQL)?
- How to translate skills to GitHub search queries (language filters)?
- How to handle partial failures (some candidates fail to load)?
- How to prioritize results when >25 matches found?
- **NEW: BigQuery integration approach** (optional feature? when to use vs GitHub Search?)
- **NEW: GraphQL batching strategy** (how many users per query? 10? 50?)
- **NEW: Primary vs fallback detection** (when to use Dependency Graph vs ensemble?)
- **NEW: Location database selection** (dr5hn/cities.json vs GeoNames vs custom?)
- **NEW: Fuzzy matching threshold** (Levenshtein distance cutoff for typos?)
- **NEW: Signal weight tuning** (optimal weights for dependencies, topics, languages, bio?)
- **NEW: Configuration file format** (YAML vs JSON vs TOML for weights/thresholds?)

**Output**: research.md with all decisions documented

## Phase 1: Design & Contracts

**Entities** (from spec.md):
1. **Candidate** (output) - ENHANCED
   - Existing Fields: github_username, name, bio, location, public_email, top_repos, languages, contribution_count, account_age_days, profile_url, avatar_url, fetched_at
   - **NEW Fields**:
     - location_parsed (LocationHierarchy object: city, state, country, match_confidence, match_level)
     - skill_confidence_scores (dict: skill → confidence score 0.0-1.0)
     - skill_signals (dict: skill → list of detection sources)
   - Validation: username required, contribution_count ≥ 0, skill_confidence_scores between 0.0-1.0

2. **SearchCriteria** (internal)
   - Derived from JobRequirement
   - Fields: required_languages, preferred_languages, location_filter, min_account_age_days, activity_level

3. **SearchResult** (metadata) - ENHANCED
   - Existing Fields: total_candidates_found, candidates_returned, search_timestamp, rate_limit_remaining, cache_hit, execution_time_ms
   - **NEW Fields**:
     - batching_used (boolean)
     - skill_detection_method (primary or fallback)
     - location_match_distribution (count of city/state/country matches)

4. **LocationHierarchy** (NEW - embedded in Candidate)
   - Fields: original_text, city, state, country, match_confidence, match_level
   - Purpose: Enable hierarchical location matching with priority scoring

5. **SkillConfidence** (NEW - embedded in Candidate)
   - Fields: skill_name, confidence_score, detection_signals, signal_weights, is_primary_detection
   - Purpose: Explain skill detection and provide transparency

**API Contracts**:
- Input: JobRequirement JSON (from Module 001 output schema)
- Output: `{"candidates": List[Candidate], "metadata": SearchResult}`

**Contract Tests**:
- `test_input_schema.py`: Validate JobRequirement has required_skills
- `test_output_schema.py`: Validate Candidate structure matches spec

**Quickstart Scenarios** (from spec.md acceptance scenarios):
1. Search for Python+FastAPI developers → verify returned candidates have those languages
2. Search with location="Tamil Nadu" → verify candidates match location
3. Search with min experience → verify account age filtering
4. Verify rate limit handling → force rate limit, check partial results
5. **NEW: Search for library-level skills** (pandas, numpy) → verify candidates use these libraries, not just Python
6. **NEW: Hierarchical location matching** → Search location="Chennai", verify city (1.0), state (0.7), country (0.3) matches
7. **NEW: Fuzzy location matching** → Profile has "Bangalor", search="Bangalore" → verify match with reduced confidence
8. **NEW: Multi-signal skill detection** → Verify skill_confidence_scores and skill_signals in output
9. **NEW: GraphQL batching** → Fetch 50 candidates, verify single batched API call used
10. **NEW: Fallback detection** → Force dependency API failure, verify ensemble scoring activates
11. **NEW: BigQuery discovery (optional)** → Configure BigQuery, query for Python devs with 20+ merged PRs, verify enrichment via GitHub API
12. **NEW: BigQuery fallback** → Disable BigQuery, verify graceful fallback to GitHub Search API

**Agent File Update**:
- Run: `.specify/scripts/bash/update-agent-context.sh claude`
- Add: Python 3.11, httpx, pydantic v2, redis, pytest, GitHub API
- Document: Module 002 - GitHub Sourcer (search candidates)

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md updated

## Phase 2: Task Planning Approach

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md`
2. Extract tasks from contracts and quickstart scenarios
3. TDD approach: tests before implementation

**Task Categories**:
- **Setup** (3 tasks): Project structure, dependencies, GitHub token config
- **Tests First** (8 tasks):
  - Contract tests (input/output validation)
  - Unit tests (github_client, search_service, cache_service, rate_limiter)
  - Integration tests (end-to-end search, caching)
- **Core Implementation** (6 tasks):
  - Candidate, SearchCriteria, SearchResult models
  - GitHub API client (search users, get profile, get repos)
  - Search service orchestration
  - Cache service (Redis integration)
  - Rate limiter
- **Integration** (2 tasks):
  - Wire all components together
  - Quickstart validation

**Ordering**:
- Models before services
- Unit tests before integration tests
- Mark [P] for parallel tasks (independent test files)

**Estimated Output**: ~20 tasks in TDD order

## Phase 3+: Future Implementation

**Phase 3**: /tasks command generates tasks.md
**Phase 4**: Execute tasks following TDD principles
**Phase 5**: Validate with quickstart.md, measure cache hit rate, verify rate limits respected

## Complexity Tracking

No constitutional violations. Module follows all 5 principles:
- Privacy-first: Public GitHub data only
- Single source: GitHub API only
- Modular: Clear input/output contracts
- No AI needed: Pure API search (AI in downstream modules)
- Transparent: Returns search metadata

## Progress Tracking

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PENDING
- [ ] All research questions answered
- [ ] Contracts defined

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
