# Tasks: GHArchive BigQuery Integration Module

**Input**: Design documents from `/specs/011-gharchive-bigquery-integration/`
**Prerequisites**: ✅ plan.md, ✅ spec.md

---

## Overview

**Module**: 011-gharchive-bigquery-integration (NEW)
**Total Tasks**: 35
**Estimated Duration**: 20-28 hours
**Approach**: TDD (Tests First, Implementation Second)

**Technology Stack**:
- Python 3.11+
- google-cloud-bigquery (BigQuery Python client)
- httpx (async HTTP client for GitHub API fallback)
- pydantic v2 (validation)
- redis (query result caching - 24 hour TTL)
- pytest + pytest-asyncio (testing)
- pyyaml (config management)

**Core Features**:
- Real-time activity discovery (GHArchive updated hourly)
- Trending developer detection (star velocity, viral repos)
- Library-specific activity filtering (pandas, React, Django)
- Contribution pattern analysis (frequency, consistency, peak times)
- Cost management ($0.31-$0.62 per 30-day query)
- Query optimization (partition filtering, column selection)
- 24-hour result caching (Redis)
- Graceful fallback to GitHub Search API (Module 002)
- Integration with Module 002 for profile enrichment

**Unique Value**: Discover developers based on what they're coding RIGHT NOW (last hour), not just their resume.

---

## Phase 3.1: Setup (5 tasks)

- [ ] **T001** Create project structure for BigQuery Sourcer module
  - Create: `src/bigquery_sourcer/` directory
  - Create subdirectories: `models/`, `services/`, `lib/`, `config/`
  - Create: `src/bigquery_sourcer/config/query_templates/` for SQL files
  - Create: `tests/bigquery_sourcer/contract/`, `tests/bigquery_sourcer/integration/`, `tests/bigquery_sourcer/unit/`
  - Verify: Directory structure matches plan.md

- [ ] **T002** Add Module 011 dependencies to pyproject.toml
  - Add to `[project.optional-dependencies]` → `bigquery = ["google-cloud-bigquery>=3.11.0"]`
  - Add: `redis >= 5.0.0` (query caching)
  - Add: `pyyaml >= 6.0` (config file parsing)
  - Verify: `pip install -e ".[bigquery]"` succeeds
  - Run: `pytest --collect-only` to verify BigQuery import works

- [ ] **T003** [P] Create SQL query templates in config/query_templates/
  - Create: `src/bigquery_sourcer/config/query_templates/activity_discovery.sql`
  - Create: `src/bigquery_sourcer/config/query_templates/trending_detection.sql`
  - Create: `src/bigquery_sourcer/config/query_templates/library_specific.sql`
  - Create: `src/bigquery_sourcer/config/query_templates/contribution_patterns.sql`
  - Add placeholders: `{table_suffix_pattern}`, `{languages}`, `{start_date}`, `{end_date}`, `{min_events}`
  - Verify: All SQL files are valid syntax (can be loaded by SQLTemplateLoader)
  - Document: Template parameters and expected outputs

- [ ] **T004** [P] Create configuration files for BigQuery
  - Create: `src/bigquery_sourcer/config/activity_thresholds.yaml` with min_events, date_ranges, star_velocity thresholds
  - Create: `src/bigquery_sourcer/config/cost_limits.yaml` with max_query_cost_usd (default: 5.0), monthly budgets
  - Add to `.env.example`: `GCP_PROJECT_ID=your-project-id`, `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json`
  - Document: BigQuery setup requirements (service account, IAM roles)
  - Verify: All config files parse correctly (YAML validation)

- [ ] **T005** [P] Create GHArchive schema reference documentation
  - Create: `src/bigquery_sourcer/lib/gharchive_schema.py` with event type constants
  - Document: Event types (PushEvent, PullRequestEvent, WatchEvent, IssuesEvent, etc.)
  - Document: Key fields (actor.login, repo.name, repo.language, type, created_at, payload)
  - Document: Table naming convention (githubarchive.day.YYYYMMDD, wildcards)
  - Add: Type hints for GHArchive event structures
  - Purpose: Reference for query building and testing

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (3 tasks)

- [ ] **T006** [P] Contract test for input schema in tests/bigquery_sourcer/contract/test_input_schema.py
  - Load: JobRequirement schema from Module 001
  - Test: Valid JobRequirement passes validation
  - Test: Missing required_skills fails validation
  - Test: JobRequirement with BigQueryConfig (optional) passes validation
  - Expected: All tests FAIL (BigQueryConfig not imported yet)

- [ ] **T007** [P] Contract test for output schema in tests/bigquery_sourcer/contract/test_output_schema.py
  - Test: Valid ActivityEnrichedCandidate object passes schema validation
  - Test: Valid BigQueryExecutionMetadata passes schema validation
  - Test: ActivityEnrichedCandidate has activity_metrics when discovered_via includes "bigquery"
  - Test: activity_score between 0-100
  - Test: TrendingMetrics fields validated (star_velocity >= 0)
  - Expected: All tests FAIL (ActivityEnrichedCandidate model doesn't exist)

- [ ] **T008** [P] Contract test for config schema in tests/bigquery_sourcer/contract/test_config_schema.py
  - Test: Valid BigQueryConfig passes validation
  - Test: Missing gcp_project_id fails validation
  - Test: max_query_cost_usd must be > 0
  - Test: default_date_range_days in [7, 14, 30, 60, 90]
  - Test: service_account_key_path points to valid file (if provided)
  - Expected: All tests FAIL (BigQueryConfig model doesn't exist)

### Unit Tests (10 tasks)

- [ ] **T009** [P] Unit test for query builder in tests/bigquery_sourcer/unit/test_query_builder.py
  - Test: JobRequirement → SQL query with correct language filters
  - Test: Template parameter substitution (table_suffix, dates, languages)
  - Test: Date range conversion (30 days → YYYYMMDD format)
  - Test: Skills to language mapping (Python → "Python", "pandas" → repo name filter)
  - Test: SQL injection protection (sanitize inputs)
  - Expected: All tests FAIL (QueryBuilder not implemented)

- [ ] **T010** [P] Unit test for cost estimator in tests/bigquery_sourcer/unit/test_cost_estimator.py
  - Test: Estimate cost for 30-day query → returns $0.31-$0.62
  - Test: Estimate cost for 90-day query → returns $0.93-$1.85
  - Test: Cost calculation formula: data_scanned_gb × 6.25
  - Test: Cost exceeds max_query_cost_usd → raises CostLimitExceededError
  - Test: Mock BigQuery dry_run to get estimated bytes
  - Expected: All tests FAIL (CostEstimator not implemented)

- [ ] **T011** [P] Unit test for query optimizer in tests/bigquery_sourcer/unit/test_query_optimizer.py
  - Test: Apply partition filter → adds `_TABLE_SUFFIX BETWEEN` clause
  - Test: Date range to table suffix pattern → "20250101" to "20250131"
  - Test: Column selection → avoids SELECT *, uses specific columns
  - Test: Result limit → adds LIMIT 1000 clause
  - Test: Optimize query reduces estimated cost by 50%+
  - Expected: All tests FAIL (QueryOptimizer not implemented)

- [ ] **T012** [P] Unit test for SQL template loader in tests/bigquery_sourcer/unit/test_sql_template_loader.py
  - Test: Load activity_discovery.sql template
  - Test: Load trending_detection.sql template
  - Test: Template not found → raises TemplateNotFoundError
  - Test: Replace placeholders with actual values
  - Test: Multiple placeholder replacement in single template
  - Expected: All tests FAIL (SQLTemplateLoader not implemented)

- [ ] **T013** [P] Unit test for query cache in tests/bigquery_sourcer/unit/test_query_cache.py
  - Test: Cache miss → returns None, sets cache after query
  - Test: Cache hit → returns cached results within TTL (24 hours)
  - Test: Cache expired → returns None after 24 hours
  - Test: Cache key generation from JobRequirement (consistent hashing)
  - Test: Cache size tracking (prevent unbounded growth)
  - Expected: All tests FAIL (QueryCache not implemented)

- [ ] **T014** [P] Unit test for activity analyzer in tests/bigquery_sourcer/unit/test_activity_analyzer.py
  - Test: BigQuery results → ActivityMetrics calculation
  - Test: Event breakdown percentages sum to 100%
  - Test: Contribution frequency (events per week)
  - Test: Consistency score calculation (regular vs bursty)
  - Test: Top repositories sorting by event count
  - Expected: All tests FAIL (ActivityAnalyzer not implemented)

- [ ] **T015** [P] Unit test for trending detector in tests/bigquery_sourcer/unit/test_trending_detector.py
  - Test: WatchEvent data → star velocity calculation (stars per day)
  - Test: Identify viral repositories (50+ stars in 90 days)
  - Test: Recent stars aggregation
  - Test: Early adopter detection (contributions within 6 months of repo creation)
  - Test: No WatchEvents → returns None for TrendingMetrics
  - Expected: All tests FAIL (TrendingDetector not implemented)

- [ ] **T016** [P] Unit test for contribution pattern analysis in tests/bigquery_sourcer/unit/test_contribution_patterns.py
  - Test: Event timeline → pattern_type classification (consistent/bursty/declining/growing)
  - Test: Peak days detection (weekday analysis)
  - Test: Streak calculation (consecutive days with events)
  - Test: Activity timeline grouping by week
  - Test: Pattern detection with sparse data (< 10 events)
  - Expected: All tests FAIL (ContributionPatternAnalyzer not implemented)

- [ ] **T017** [P] Unit test for GHArchive schema parser in tests/bigquery_sourcer/unit/test_gharchive_schema.py
  - Test: Parse PushEvent payload → extract commit count, repo name
  - Test: Parse PullRequestEvent payload → extract PR action (opened/closed/merged)
  - Test: Parse WatchEvent payload → extract starred repo
  - Test: Parse IssuesEvent payload → extract issue action
  - Test: Handle missing fields gracefully (return None, not crash)
  - Expected: All tests FAIL (GHArchiveSchemaParser not implemented)

- [ ] **T018** [P] Unit test for config loader in tests/bigquery_sourcer/unit/test_config_loader.py
  - Test: Load activity_thresholds.yaml with all required thresholds
  - Test: Load cost_limits.yaml with max costs
  - Test: Load environment variables (GCP_PROJECT_ID, credentials path)
  - Test: Missing config file → uses default values
  - Test: Invalid YAML → raises clear ConfigError
  - Expected: All tests FAIL (ConfigLoader not implemented)

### Integration Tests (10 tasks)

- [ ] **T019** [P] Integration test for BigQuery authentication in tests/bigquery_sourcer/integration/test_bigquery_auth.py
  - Mock: BigQuery client initialization
  - Test: Valid service account → client created successfully
  - Test: Missing credentials → raises clear AuthenticationError
  - Test: Invalid project ID → raises ProjectNotFoundError
  - Test: Test query execution (SELECT 1) → verifies connection
  - Expected: All tests FAIL (BigQueryClient not implemented)

- [ ] **T020** [P] Integration test for activity discovery query in tests/bigquery_sourcer/integration/test_activity_query.py
  - Mock: BigQuery query response with PushEvent data
  - Test: Search Python developers → returns usernames with activity metrics
  - Test: Filter by min_events (10+) → excludes low-activity users
  - Test: Date range (last 30 days) → partition filter applied correctly
  - Test: Query completes within 60 seconds
  - Test: Returns top 1000 candidates by event count
  - Expected: All tests FAIL (activity discovery query not implemented)

- [ ] **T021** [P] Integration test for trending detection query in tests/bigquery_sourcer/integration/test_trending_query.py
  - Mock: BigQuery query response with WatchEvent data
  - Test: Find repositories with 50+ stars in 90 days
  - Test: Calculate star velocity (stars per day)
  - Test: Identify contributors to viral repos
  - Test: Query completes within 90 seconds
  - Test: Returns trending metrics for each candidate
  - Expected: All tests FAIL (trending detection query not implemented)

- [ ] **T022** [P] Integration test for library-specific query in tests/bigquery_sourcer/integration/test_library_query.py
  - Mock: BigQuery query response filtered by repo name keywords
  - Test: Search "pandas" → finds repos with "pandas" in name/description
  - Test: Search "fastapi" → finds repos with "fastapi" in name
  - Test: Multiple libraries (pandas AND numpy) → finds overlapping contributors
  - Test: Case-insensitive matching
  - Expected: All tests FAIL (library-specific query not implemented)

- [ ] **T023** [P] Integration test for cost tracking in tests/bigquery_sourcer/integration/test_cost_tracking.py
  - Mock: BigQuery job with bytes_processed metadata
  - Test: Execute query → cost calculated from bytes_processed
  - Test: Cost logged to database with timestamp
  - Test: estimated_cost_usd matches actual cost within 10%
  - Test: Cost exceeds limit → query blocked before execution
  - Test: Query metadata includes query_job_id for tracking
  - Expected: All tests FAIL (cost tracking not implemented)

- [ ] **T024** [P] Integration test for query caching in tests/bigquery_sourcer/integration/test_query_caching.py
  - Test: First query → cache_hit=False, results cached
  - Test: Second identical query within 24 hours → cache_hit=True, cost=$0
  - Test: Query with different parameters → cache_miss
  - Test: Cache expiration after 24 hours → cache_miss, re-query
  - Test: Cache hit reduces response time from 60s to <2s
  - Expected: All tests FAIL (query caching not implemented)

- [ ] **T025** [P] Integration test for Module 002 integration in tests/bigquery_sourcer/integration/test_module_002_integration.py
  - Mock: BigQuery returns 100 usernames
  - Mock: GitHub API enrichment from Module 002
  - Test: BigQuery usernames → passed to Module 002 GitHubClient for enrichment
  - Test: Merge activity_metrics from BigQuery with profile data from GitHub API
  - Test: Deduplication (candidate in both BigQuery and GitHub Search)
  - Test: discovered_via field set correctly ("bigquery", "github_search", "both")
  - Test: Activity score calculated from BigQuery metrics
  - Expected: All tests FAIL (Module 002 integration not implemented)

- [ ] **T026** [P] Integration test for graceful fallback in tests/bigquery_sourcer/integration/test_fallback.py
  - Test: BigQuery credentials missing → falls back to GitHub Search API (Module 002)
  - Test: BigQuery authentication fails → falls back gracefully
  - Test: BigQuery query timeout → falls back with warning
  - Test: BigQuery quota exceeded → falls back and logs error
  - Test: Fallback candidates have discovered_via="github_search"
  - Test: No disruption to user (seamless fallback)
  - Expected: All tests FAIL (fallback logic not implemented)

- [ ] **T027** [P] Integration test for performance benchmarks in tests/bigquery_sourcer/integration/test_performance.py
  - Test: 30-day query completes within 60 seconds (target)
  - Test: 90-day query completes within 90 seconds
  - Test: Cache hit response time <2 seconds
  - Test: Concurrent queries (5 parallel) → no blocking
  - Test: Query optimization reduces data scanned to <100 GB
  - Expected: All tests FAIL (performance not yet measured)

- [ ] **T028** [P] Integration test for error handling in tests/bigquery_sourcer/integration/test_error_handling.py
  - Test: Network timeout → retry 3 times with exponential backoff
  - Test: BigQuery API error (500) → retry and log error
  - Test: Invalid SQL query → raises QuerySyntaxError
  - Test: GHArchive table not found (future date) → returns empty results
  - Test: Partial results on error → returns successful candidates only
  - Expected: All tests FAIL (error handling not implemented)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (6 tasks)

- [ ] **T029** [P] Create ActivityEnrichedCandidate model in src/bigquery_sourcer/models/activity_enriched_candidate.py
  - Implement: ActivityEnrichedCandidate Pydantic model per data-model.md
  - Extends: Candidate from Module 002 (github_username, name, bio, location, profile_url)
  - NEW Fields: activity_metrics, trending_metrics, contribution_patterns, discovered_via, activity_score, data_freshness
  - Add validators: activity_score between 0-100, discovered_via in ["bigquery", "github_search", "both"]
  - Add validator: activity_metrics required if discovered_via includes "bigquery"
  - Verify: tests/bigquery_sourcer/contract/test_output_schema.py ActivityEnrichedCandidate tests pass

- [ ] **T030** [P] Create ActivityMetrics model in src/bigquery_sourcer/models/activity_metrics.py
  - Implement: ActivityMetrics Pydantic model (embedded in ActivityEnrichedCandidate)
  - Fields: total_events, event_breakdown, unique_repositories, contribution_frequency, active_days, consistency_score, top_repositories
  - Add validator: event_breakdown percentages sum to 100
  - Add validator: consistency_score between 0-1
  - Add validator: total_events >= 0, unique_repositories >= 0
  - Verify: ActivityMetrics can be embedded in ActivityEnrichedCandidate

- [ ] **T031** [P] Create TrendingMetrics model in src/bigquery_sourcer/models/trending_metrics.py
  - Implement: TrendingMetrics Pydantic model (optional, embedded in ActivityEnrichedCandidate)
  - Fields: star_velocity, recent_stars, viral_repositories, follower_growth, early_adopter_signals
  - Add validator: star_velocity >= 0, recent_stars >= 0
  - Add validator: viral_repositories is list of dicts with repo, stars, period_days
  - Mark as optional (can be None if trending detection disabled)
  - Verify: TrendingMetrics can be optionally embedded in ActivityEnrichedCandidate

- [ ] **T032** [P] Create ContributionPatterns model in src/bigquery_sourcer/models/contribution_patterns.py
  - Implement: ContributionPatterns Pydantic model (embedded in ActivityEnrichedCandidate)
  - Fields: pattern_type, peak_days, peak_hours, longest_streak, current_streak, activity_timeline
  - Add validator: pattern_type in ["consistent", "bursty", "declining", "growing"]
  - Add validator: streaks >= 0
  - Add validator: peak_days are valid weekdays
  - Verify: ContributionPatterns can be embedded in ActivityEnrichedCandidate

- [ ] **T033** [P] Create BigQueryExecutionMetadata model in src/bigquery_sourcer/models/bigquery_execution_metadata.py
  - Implement: BigQueryExecutionMetadata Pydantic model
  - Fields: query_cost_usd, estimated_cost_usd, data_scanned_gb, query_duration_ms, date_range, cache_hit, candidates_found, candidates_returned, table_suffix_pattern, query_job_id
  - Add validators: costs >= 0, query_duration_ms >= 0
  - Add validator: candidates_found >= candidates_returned
  - Purpose: Returned alongside List[ActivityEnrichedCandidate]
  - Verify: tests/bigquery_sourcer/contract/test_output_schema.py BigQueryExecutionMetadata tests pass

- [ ] **T034** [P] Create BigQueryConfig model in src/bigquery_sourcer/models/bigquery_config.py
  - Implement: BigQueryConfig Pydantic model
  - Fields: gcp_project_id, service_account_key_path, max_query_cost_usd, default_date_range_days, cache_ttl_hours, enable_trending_detection, max_candidates_before_enrichment, query_timeout_seconds
  - Add validators: max_query_cost_usd > 0, default_date_range_days in [7, 14, 30, 60, 90]
  - Add validator: cache_ttl_hours > 0, query_timeout_seconds > 0
  - Add defaults: max_query_cost_usd=5.0, default_date_range_days=30, cache_ttl_hours=24
  - Verify: tests/bigquery_sourcer/contract/test_config_schema.py BigQueryConfig tests pass

### Libraries (3 tasks)

- [ ] **T035** [P] Create QueryCache in src/bigquery_sourcer/lib/query_cache.py
  - Implement: QueryCache class with Redis backend
  - Methods: get(cache_key), set(cache_key, results, ttl=24h), invalidate(cache_key)
  - Method: generate_cache_key(JobRequirement) → consistent hash
  - Add: TTL enforcement (24 hours default, configurable)
  - Add: Cache size tracking (optional, log warnings if >1GB)
  - Verify: tests/bigquery_sourcer/unit/test_query_cache.py passes
  - Verify: tests/bigquery_sourcer/integration/test_query_caching.py passes

- [ ] **T036** [P] Create SQLTemplateLoader in src/bigquery_sourcer/lib/sql_template_loader.py
  - Implement: SQLTemplateLoader class
  - Method: load_template(template_name) → returns SQL string
  - Method: replace_placeholders(sql, params) → substitutes {placeholders}
  - Add: Template path resolution (config/query_templates/*.sql)
  - Add: SQL injection protection (validate/sanitize params)
  - Raise: TemplateNotFoundError if template file missing
  - Verify: tests/bigquery_sourcer/unit/test_sql_template_loader.py passes

- [ ] **T037** [P] Create GHArchiveSchemaParser in src/bigquery_sourcer/lib/gharchive_schema.py
  - Implement: GHArchiveSchemaParser class with event type parsers
  - Method: parse_push_event(payload) → extract commits, repo
  - Method: parse_pull_request_event(payload) → extract action, PR metadata
  - Method: parse_watch_event(payload) → extract starred repo
  - Method: parse_issues_event(payload) → extract action, issue metadata
  - Add: Type hints for GHArchive event structures (use TypedDict or Pydantic)
  - Verify: tests/bigquery_sourcer/unit/test_gharchive_schema.py passes

### Services (7 tasks)

- [ ] **T038** [P] Create BigQueryClient in src/bigquery_sourcer/services/bigquery_client.py
  - Implement: BigQueryClient class wrapping google.cloud.bigquery.Client
  - Method: __init__(config: BigQueryConfig) → initialize client with service account
  - Method: execute_query(sql: str, timeout: int) → returns query results
  - Method: estimate_query_cost(sql: str) → returns estimated cost in USD (dry_run)
  - Add: Authentication via service account JSON key
  - Add: Query timeout enforcement (60 seconds default)
  - Add: Error handling (AuthenticationError, QuerySyntaxError, TimeoutError)
  - Verify: tests/bigquery_sourcer/integration/test_bigquery_auth.py passes

- [ ] **T039** [P] Create QueryBuilder in src/bigquery_sourcer/services/query_builder.py
  - Implement: QueryBuilder class
  - Method: build_activity_discovery_query(job_req: JobRequirement, config: BigQueryConfig) → returns SQL
  - Method: build_trending_detection_query(job_req: JobRequirement, config: BigQueryConfig) → returns SQL
  - Method: build_library_specific_query(job_req: JobRequirement, library: str, config: BigQueryConfig) → returns SQL
  - Add: Skills → language mapping (Python, JavaScript, etc.)
  - Add: Date range → table suffix conversion (30 days → "20250101" to "20250131")
  - Add: Template parameter substitution via SQLTemplateLoader
  - Verify: tests/bigquery_sourcer/unit/test_query_builder.py passes

- [ ] **T040** [P] Create CostEstimator in src/bigquery_sourcer/services/cost_estimator.py
  - Implement: CostEstimator class
  - Method: estimate_cost(sql: str, client: BigQueryClient) → returns estimated cost in USD
  - Method: enforce_cost_limit(estimated_cost: float, max_cost: float) → raises CostLimitExceededError if exceeded
  - Method: log_cost(query_id: str, estimated: float, actual: float) → logs to database
  - Add: Cost calculation formula: bytes_processed × 6.25 / 1TB
  - Add: Cost tracking to database (query_id, timestamp, estimated, actual)
  - Verify: tests/bigquery_sourcer/unit/test_cost_estimator.py passes
  - Verify: tests/bigquery_sourcer/integration/test_cost_tracking.py passes

- [ ] **T041** [P] Create QueryOptimizer in src/bigquery_sourcer/services/query_optimizer.py
  - Implement: QueryOptimizer class
  - Method: apply_partition_filter(sql: str, start_date: str, end_date: str) → adds `_TABLE_SUFFIX BETWEEN`
  - Method: optimize_column_selection(sql: str) → ensures specific columns, not SELECT *
  - Method: apply_result_limit(sql: str, limit: int) → adds LIMIT clause
  - Method: estimate_optimization_savings(original_sql: str, optimized_sql: str) → returns cost reduction %
  - Verify: tests/bigquery_sourcer/unit/test_query_optimizer.py passes

- [ ] **T042** [P] Create ActivityAnalyzer in src/bigquery_sourcer/services/activity_analyzer.py
  - Implement: ActivityAnalyzer class
  - Method: analyze_activity(bigquery_results: List[dict]) → returns Dict[str, ActivityMetrics]
  - Method: calculate_event_breakdown(events: List) → returns dict of percentages by type
  - Method: calculate_contribution_frequency(events: List, days: int) → returns events per week
  - Method: calculate_consistency_score(events: List) → returns 0-1 score (regular vs bursty)
  - Method: extract_top_repositories(events: List) → returns sorted list by event count
  - Verify: tests/bigquery_sourcer/unit/test_activity_analyzer.py passes

- [ ] **T043** [P] Create TrendingDetector in src/bigquery_sourcer/services/trending_detector.py
  - Implement: TrendingDetector class
  - Method: detect_trending(bigquery_results: List[dict]) → returns Dict[str, TrendingMetrics]
  - Method: calculate_star_velocity(watch_events: List, days: int) → returns stars per day
  - Method: identify_viral_repositories(watch_events: List, threshold: int) → returns repos with 50+ stars
  - Method: detect_early_adopters(push_events: List, repo_creation_dates: Dict) → identifies contributions within 6 months
  - Add: Aggregation of WatchEvents per repository
  - Verify: tests/bigquery_sourcer/unit/test_trending_detector.py passes
  - Verify: tests/bigquery_sourcer/integration/test_trending_query.py passes

- [ ] **T044** [P] Create IntegrationService in src/bigquery_sourcer/services/integration_service.py
  - Implement: IntegrationService class to merge BigQuery + Module 002 data
  - Method: merge_activity_with_profiles(activity_data: Dict, profiles: List[Candidate]) → List[ActivityEnrichedCandidate]
  - Method: deduplicate_candidates(bigquery: List, github_search: List) → returns unique candidates
  - Method: fallback_to_github_search(job_req: JobRequirement) → calls Module 002 SearchService
  - Method: enrich_with_github_api(usernames: List[str]) → calls Module 002 GitHubClient
  - Add: discovered_via field management ("bigquery", "github_search", "both")
  - Add: Activity score calculation from BigQuery metrics
  - Verify: tests/bigquery_sourcer/integration/test_module_002_integration.py passes
  - Verify: tests/bigquery_sourcer/integration/test_fallback.py passes

---

## Phase 3.4: Integration & Validation (3 tasks)

- [ ] **T045** Wire all components together in src/bigquery_sourcer/__init__.py
  - Create: Main orchestrator class BigQuerySourcer
  - Method: source_candidates(job_req: JobRequirement, config: BigQueryConfig) → List[ActivityEnrichedCandidate]
  - Integration flow:
    1. Load config (ConfigLoader)
    2. Check cache (QueryCache)
    3. Build query (QueryBuilder)
    4. Estimate cost (CostEstimator)
    5. Optimize query (QueryOptimizer)
    6. Execute query (BigQueryClient)
    7. Analyze activity (ActivityAnalyzer)
    8. Detect trending (TrendingDetector)
    9. Enrich profiles (IntegrationService + Module 002)
    10. Cache results (QueryCache)
  - Add: Graceful fallback to Module 002 on any error
  - Verify: All integration tests pass

- [ ] **T046** Validate with quickstart scenarios from plan.md
  - Test: BigQuery authentication → verify connection succeeds
  - Test: Activity discovery query → verify results within 60 seconds
  - Test: Cost estimation and blocking → verify $7 query blocked
  - Test: Cost tracking → verify actual cost logged
  - Test: Caching → verify second query hits cache, costs $0
  - Test: Trending detection → verify star velocity calculated
  - Test: Library-specific search → verify pandas users found
  - Test: Module 002 integration → verify profiles enriched
  - Test: Graceful fallback → verify GitHub Search API used when BigQuery disabled
  - Test: Merge results → verify deduplication works
  - Test: Activity pattern analysis → verify consistency_score calculated
  - Test: Performance → verify 30-day query completes <60s
  - Test: Error handling → verify retry logic (3 attempts)
  - Test: Query optimization → verify data scanned <100 GB
  - Document: All quickstart scenarios pass ✅

- [ ] **T047** [P] Create production readiness checklist
  - Document: BigQuery setup guide (service account creation, IAM roles)
  - Document: Cost monitoring dashboard setup
  - Document: Query performance benchmarks
  - Document: Fallback behavior and error recovery
  - Add: Monitoring hooks (cost tracking, performance logging)
  - Add: Alerting recommendations (budget exceeded, high failure rate)
  - Verify: Module can be deployed to production
  - Verify: Integration with Module 002 and Module 003 (Ranking Engine)

---

## Phase 3.5: Documentation & Testing Summary

### Testing Summary

**Total Tests**: ~60 tests
- Contract tests: 9 tests (3 tasks)
- Unit tests: 25 tests (10 tasks)
- Integration tests: 20 tests (10 tasks)
- Quickstart validation: 14 scenarios (1 task)

**Expected Test Results**:
- Phase 3.2 (Tests First): All tests FAIL ❌ (expected, no implementation yet)
- Phase 3.3 (Implementation): Tests progressively PASS ✅
- Phase 3.4 (Integration): All tests PASS ✅

### Documentation Checklist

- [ ] All models documented with docstrings
- [ ] All services documented with usage examples
- [ ] SQL templates documented with parameter descriptions
- [ ] BigQuery setup guide complete
- [ ] Cost management documentation complete
- [ ] Integration guide with Module 002 complete
- [ ] Fallback behavior documented
- [ ] Performance benchmarks documented
- [ ] Error handling guide complete

---

## Progress Tracking

**Phase Status**:
- [ ] Phase 3.1: Setup complete (5 tasks)
- [ ] Phase 3.2: Tests First complete (23 tasks) ⚠️ All MUST FAIL
- [ ] Phase 3.3: Core Implementation complete (16 tasks)
- [ ] Phase 3.4: Integration & Validation complete (3 tasks)
- [ ] Phase 3.5: Documentation complete

**Key Milestones**:
- [ ] BigQuery authentication working
- [ ] First successful query executed
- [ ] Cost estimation accurate (within 10% of actual)
- [ ] Cache working (>50% hit rate on repeated queries)
- [ ] Module 002 integration working (merge activity + profile data)
- [ ] Fallback to GitHub Search API working
- [ ] Activity metrics in Ranking Engine (Module 003)
- [ ] Production deployment ready

**Performance Targets**:
- [ ] 30-day query: <60 seconds ✅
- [ ] 90-day query: <90 seconds ✅
- [ ] Cache hit: <2 seconds ✅
- [ ] Query cost: <$5 per query ✅
- [ ] Cost accuracy: within 10% of estimate ✅
- [ ] Data scanned: <100 GB per query ✅

---

## Notes

**TDD Compliance**:
- ✅ Phase 3.2 MUST be completed before Phase 3.3
- ✅ All tests MUST FAIL before implementation begins
- ✅ Implement only enough code to make tests pass
- ✅ Refactor after tests pass

**Parallel Tasks**:
- Tasks marked [P] can be worked on in parallel (no dependencies)
- Contract tests, unit tests, and integration tests within same phase can be parallel
- Models can be implemented in parallel after tests are written

**Optional Features**:
- Contribution pattern analysis (peak times, streaks) can be Phase 2
- Early adopter detection can be Phase 2
- Advanced trending metrics can be Phase 2
- Focus on core activity discovery and cost management first

**Integration Dependencies**:
- Requires Module 002 (GitHub Sourcer) for profile enrichment
- Integrates with Module 003 (Ranking Engine) for activity-based ranking
- Uses Module 001 output (JobRequirement) as input

---

**Ready for Implementation**: ✅ Yes (all tasks defined, TDD approach clear)
**Estimated Completion**: 20-28 hours (3-4 weeks part-time)
**Next Step**: Begin T001 (Create project structure)
