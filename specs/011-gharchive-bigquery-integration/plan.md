# Implementation Plan: GHArchive BigQuery Integration Module

**Branch**: `011-gharchive-bigquery-integration` | **Date**: 2025-11-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-gharchive-bigquery-integration/spec.md`

## Summary
GHArchive BigQuery Integration module provides real-time GitHub activity discovery by querying the GHArchive public dataset (updated hourly) to find developers based on their actual contribution patterns, not just static profiles. Complements existing GitHub Search API (Module 002) with activity-based intelligence.

**Core Capabilities**:
- **Real-Time Activity Discovery** - Query last 7-90 days of GitHub events (commits, PRs, issues, stars) from GHArchive
- **Trending Developer Detection** - Identify rising talent with star velocity tracking and viral repository detection
- **Library-Specific Activity** - Find developers actively contributing to pandas, React, Django in the last 30 days
- **Contribution Pattern Analysis** - Calculate event frequency, consistency, repository diversity, peak times
- **Cost Management** - Pre-execution cost estimation, configurable limits ($5 default), 24-hour caching
- **Query Optimization** - Partition filtering, column selection, result limits to minimize data scanned (50-100 GB typical)
- **Graceful Fallback** - Automatic fallback to GitHub Search API (Module 002) if BigQuery unavailable
- **Integration Ready** - Merges BigQuery activity data with GitHub profile enrichment seamlessly

**Unique Value**: Discover developers based on what they're coding RIGHT NOW (last hour), not just their resume.

**Cost Profile**: $0.31-$0.62 per 30-day query (~50-100 GB scanned), 1 TB/month free tier

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**:
- google-cloud-bigquery (BigQuery Python client)
- httpx (async HTTP for GitHub API fallback)
- pydantic v2 (validation)
- asyncio (concurrent processing)
- redis (optional query result caching)

**Storage**:
- PostgreSQL for activity metrics persistence
- Redis for 24-hour query result caching

**Testing**: pytest + pytest-asyncio + pytest-mock
**Target Platform**: Linux server / Docker container
**Project Type**: Single module (part of larger GitHire pipeline)
**Performance Goals**:
- Query execution: <60 seconds for 30-day range
- Cache hits: <2 seconds
- Cost per query: <$5 (configurable)
- Result limit: 1000 candidates before enrichment

**Constraints**:
- BigQuery pricing: $6.25/TB scanned
- BigQuery rate limits: 100 concurrent queries per project
- GHArchive update frequency: Hourly
- Integration with Module 002 for profile enrichment

**Scale/Scope**: Handle 100+ queries per day, $10-30 monthly budget typical usage

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development
- [x] No LLM required for this module (pure BigQuery data access)
- [x] Module outputs to Ranking Engine (Module 003) which may use activity signals

### II. Privacy-First Architecture
- [x] Only public GitHub events from GHArchive (public dataset)
- [x] No private repository data accessed
- [x] Respects GitHub Terms of Service for bulk data usage
- [x] No circumvention of rate limits or privacy protections
- [x] GDPR compliant (public data, clear retention policies)

### III. Single Source of Truth
- [x] GHArchive BigQuery dataset as primary source
- [x] Fallback to GitHub Search API (Module 002) if BigQuery unavailable
- [x] No third-party enrichment services
- [x] Data attribution to GHArchive in all outputs

### IV. Transparency & Explainability
- [x] Returns metadata: query_cost_usd, data_scanned_gb, query_duration_ms, cache_hit
- [x] Activity metrics include source attribution (BigQuery vs GitHub Search)
- [x] Transparent cost tracking and budget enforcement
- [x] Clear indication of which candidates were discovered via activity vs profile search

### V. Modular Architecture
- [x] Standalone module with clear input/output interface
- [x] Input: JobRequirement JSON (from Module 001)
- [x] Output: List[ActivityEnrichedCandidate] + BigQueryExecutionMetadata
- [x] Independently testable with mock BigQuery responses
- [x] Graceful integration with Module 002 (GitHub Sourcer)

**Constitution Status**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/011-gharchive-bigquery-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (JSON schemas)
│   ├── input-schema.json
│   ├── output-schema.json
│   └── config-schema.json
├── queries/             # Phase 1 output (SQL templates)
│   ├── activity_discovery.sql
│   ├── trending_detection.sql
│   ├── library_specific.sql
│   └── contribution_patterns.sql
└── tasks.md             # Phase 2 output (/tasks command)
```

### Source Code (repository root)
```
src/bigquery_sourcer/
├── models/
│   ├── activity_enriched_candidate.py  # NEW: ActivityEnrichedCandidate entity
│   ├── activity_metrics.py             # NEW: ActivityMetrics embedded model
│   ├── trending_metrics.py             # NEW: TrendingMetrics embedded model
│   ├── contribution_patterns.py        # NEW: ContributionPatterns embedded model
│   ├── bigquery_execution_metadata.py  # NEW: Query execution metadata
│   └── bigquery_config.py              # NEW: Configuration model
├── services/
│   ├── bigquery_client.py              # NEW: Google BigQuery API wrapper
│   ├── activity_analyzer.py            # NEW: Analyze GitHub events for patterns
│   ├── trending_detector.py            # NEW: Calculate star velocity, viral repos
│   ├── query_builder.py                # NEW: Build SQL queries from JobRequirement
│   ├── cost_estimator.py               # NEW: Pre-execution cost estimation
│   ├── query_optimizer.py              # NEW: Apply partition filters, column selection
│   └── integration_service.py          # NEW: Merge BigQuery + GitHub API data
├── lib/
│   ├── query_cache.py                  # NEW: 24-hour query result caching (Redis)
│   ├── sql_template_loader.py          # NEW: Load SQL from template files
│   └── gharchive_schema.py             # NEW: GHArchive event schema definitions
├── config/
│   ├── query_templates/                # NEW: Configurable SQL templates
│   │   ├── activity_discovery.sql
│   │   ├── trending_detection.sql
│   │   └── library_specific.sql
│   ├── activity_thresholds.yaml        # NEW: Minimum events, date ranges
│   └── cost_limits.yaml                # NEW: Max cost per query, monthly budgets
└── __init__.py                         # Module exports

tests/bigquery_sourcer/
├── contract/
│   ├── test_input_schema.py            # Validate JobRequirement contract
│   ├── test_output_schema.py           # Validate ActivityEnrichedCandidate contract
│   └── test_config_schema.py           # Validate BigQueryConfig contract
├── integration/
│   ├── test_bigquery_query.py          # Test against real BigQuery (limited)
│   ├── test_activity_analysis.py       # Test event pattern analysis
│   ├── test_trending_detection.py      # Test star velocity calculation
│   ├── test_module_002_integration.py  # Test merge with GitHub Sourcer
│   └── test_cost_tracking.py           # Test cost estimation and enforcement
└── unit/
    ├── test_query_builder.py           # Mock query construction
    ├── test_cost_estimator.py          # Test cost calculation logic
    ├── test_query_optimizer.py         # Test partition filter generation
    ├── test_query_cache.py             # Test caching behavior
    └── test_sql_template_loader.py     # Test template loading
```

**Structure Decision**: Single project structure with modular services. BigQuery Sourcer is Module 011 in the GitHire pipeline, complementing Module 002 (GitHub Sourcer) with activity-based discovery.

## Phase 0: Outline & Research

**Research Tasks**:

### BigQuery Core
1. **BigQuery Python Client API** - Study google-cloud-bigquery library methods, authentication
2. **Query Execution Patterns** - Synchronous vs asynchronous query patterns with ThreadPoolExecutor
3. **Cost Estimation API** - Use `query.estimated_bytes_processed` before execution
4. **Query Jobs Management** - Track job IDs, handle retries, monitor completion

### GHArchive Dataset
5. **GHArchive Schema** - Study event types (PushEvent, PullRequestEvent, WatchEvent, etc.)
6. **Table Structure** - Daily tables (`githubarchive.day.YYYYMMDD`), monthly tables, wildcards
7. **Event Payload Structure** - Analyze JSON payloads for each event type
8. **Data Completeness** - Understand gaps, missing hours, data quality issues

### Query Optimization
9. **Partition Filtering** - Use `_TABLE_SUFFIX BETWEEN` for date range filtering
10. **Column Selection** - Avoid `SELECT *`, choose specific fields to minimize data scanned
11. **Result Limits** - Use `LIMIT` clauses to cap result sets
12. **Clustering vs Partitioning** - Understand when to use each (GHArchive is pre-partitioned by date)

### Cost Management
13. **Cost Calculation Formula** - Data scanned (GB) × $6.25 = cost
14. **Free Tier** - 1 TB/month free query processing
15. **Cost Tracking** - Log all queries with costs to database for billing
16. **Budget Enforcement** - Block queries exceeding configured cost limits

### Caching Strategy
17. **Redis Caching** - 24-hour TTL for query results, cache key structure
18. **Cache Invalidation** - When to invalidate (manual refresh requests)
19. **Cache Hit Metrics** - Track cache hit rate for cost savings analysis

### Integration with Module 002
20. **Merge Strategy** - Combine BigQuery usernames with GitHub API profile data
21. **Deduplication** - Handle candidates found in both BigQuery and GitHub Search
22. **Fallback Logic** - Seamlessly use Module 002 if BigQuery fails or is disabled
23. **Data Enrichment Flow** - Activity metrics → profile enrichment → ranking

### Performance
24. **Concurrent Queries** - Use ThreadPoolExecutor for parallel query execution
25. **Timeout Handling** - Set query timeouts (60 seconds default)
26. **Error Handling** - Retry logic for transient failures (3 attempts, exponential backoff)

### Security & Authentication
27. **Service Account Setup** - GCP service account with BigQuery User role
28. **Credential Management** - Store service account JSON securely (environment variable path)
29. **Project ID Configuration** - GCP project ID for BigQuery API calls

**Key Decisions to Make**:

### Query Design
- **Which event types to query?** (PushEvent, PullRequestEvent prioritized; WatchEvent for trending)
- **How to filter by language?** (Use `repo.language` field vs repository name patterns)
- **How to detect library usage?** (Repository name keywords, commit file paths if available)
- **How many days to query by default?** (30 days balances recency and cost)

### Cost Management
- **Default cost limit per query?** ($5 blocks expensive queries)
- **Monthly budget tracking?** (Per-user or per-project budgets)
- **Cache TTL?** (24 hours balances freshness and cost savings)

### Performance
- **Query timeout?** (60 seconds for 30-day queries, 90 seconds for 90-day)
- **Result limit before enrichment?** (1000 candidates caps GitHub API calls)
- **Concurrent query limit?** (5-10 parallel queries for batch processing)

### Integration
- **When to use BigQuery vs GitHub Search?** (BigQuery for activity filters, GitHub Search for profile-based)
- **How to merge results?** (Deduplicate by username, prioritize activity data)
- **Fallback trigger?** (Authentication failure, quota exceeded, query timeout)

### Configuration
- **SQL template location?** (config/query_templates/*.sql for editability)
- **Threshold configuration?** (YAML for min_events, date_ranges, star_velocity)
- **Cost limit configuration?** (YAML per-user or global limits)

**Output**: research.md with all decisions documented, SQL query examples tested in BigQuery console

## Phase 1: Design & Contracts

**Entities** (from spec.md):

### 1. ActivityEnrichedCandidate (Output) - NEW
Extends Candidate from Module 002 with activity enrichment
- **Base Fields** (from Module 002): github_username, name, bio, location, profile_url, top_repos, languages
- **NEW Fields**:
  - activity_metrics (ActivityMetrics object)
  - trending_metrics (TrendingMetrics object, optional)
  - contribution_patterns (ContributionPatterns object)
  - discovered_via (enum: "bigquery", "github_search", "both")
  - activity_score (float 0-100, weighted from event frequency and quality)
  - data_freshness (datetime, when GHArchive data was last updated)
- **Validation**:
  - activity_score between 0-100
  - activity_metrics required if discovered_via includes "bigquery"
  - data_freshness within last 24 hours

### 2. ActivityMetrics (Embedded) - NEW
- **Fields**:
  - total_events (int, total GitHub events in time period)
  - event_breakdown (dict, percentage by type: {"PushEvent": 65%, "PullRequestEvent": 25%})
  - unique_repositories (int, number of different repos contributed to)
  - contribution_frequency (float, average events per week)
  - active_days (int, number of days with at least one event)
  - consistency_score (float 0-1, measures regular vs bursty contributions)
  - top_repositories (list of dicts: [{"repo": "owner/name", "event_count": 50}])
- **Validation**:
  - total_events >= 0
  - event_breakdown percentages sum to 100
  - consistency_score between 0-1

### 3. TrendingMetrics (Embedded, Optional) - NEW
- **Fields**:
  - star_velocity (float, stars gained per day)
  - recent_stars (int, stars gained in time period)
  - viral_repositories (list of dicts: [{"repo": "owner/name", "stars": 150, "period_days": 90}])
  - follower_growth (int, new followers in time period, if available from Events API)
  - early_adopter_signals (list of strings: ["FastAPI", "Astro"])
- **Validation**:
  - star_velocity >= 0
  - recent_stars >= 0

### 4. ContributionPatterns (Embedded) - NEW
- **Fields**:
  - pattern_type (enum: "consistent", "bursty", "declining", "growing")
  - peak_days (list of weekdays: ["Monday", "Wednesday"])
  - peak_hours (list of hours: [9, 10, 14, 15], if timezone data available)
  - longest_streak (int, consecutive days with contributions)
  - current_streak (int, ongoing consecutive days)
  - activity_timeline (list of dicts: [{"week": "2025-W10", "events": 45}])
- **Validation**:
  - pattern_type is valid enum value
  - streaks >= 0

### 5. BigQueryExecutionMetadata (Output Metadata) - NEW
- **Fields**:
  - query_cost_usd (float, actual cost of query execution)
  - estimated_cost_usd (float, pre-execution estimate)
  - data_scanned_gb (float, gigabytes of data scanned)
  - query_duration_ms (int, execution time in milliseconds)
  - date_range (dict: {"start_date": "2025-01-01", "end_date": "2025-01-31"})
  - cache_hit (bool, whether results came from cache)
  - candidates_found (int, total usernames discovered)
  - candidates_returned (int, after filtering and deduplication)
  - table_suffix_pattern (string, which GHArchive tables were queried)
  - query_job_id (string, BigQuery job ID for tracking)
- **Validation**:
  - costs >= 0
  - query_duration_ms >= 0
  - candidates_found >= candidates_returned

### 6. BigQueryConfig (Configuration) - NEW
- **Fields**:
  - gcp_project_id (string, Google Cloud Project ID)
  - service_account_key_path (string, path to JSON key file)
  - max_query_cost_usd (float, maximum allowed cost per query, default: 5.0)
  - default_date_range_days (int, default lookback period, default: 30)
  - cache_ttl_hours (int, cache duration, default: 24)
  - enable_trending_detection (bool, calculate star velocity, default: true)
  - max_candidates_before_enrichment (int, limit before GitHub API enrichment, default: 500)
  - query_timeout_seconds (int, BigQuery query timeout, default: 60)
- **Validation**:
  - max_query_cost_usd > 0
  - default_date_range_days in [7, 14, 30, 60, 90]
  - cache_ttl_hours > 0

**API Contracts**:
- **Input**: JobRequirement JSON (from Module 001 output schema) + optional BigQueryConfig
- **Output**: `{"candidates": List[ActivityEnrichedCandidate], "metadata": BigQueryExecutionMetadata}`

**Contract Tests**:
- `test_input_schema.py`: Validate JobRequirement has required_skills
- `test_output_schema.py`: Validate ActivityEnrichedCandidate structure matches spec
- `test_config_schema.py`: Validate BigQueryConfig has required fields

**SQL Query Templates** (Phase 1 output):

### Template 1: Activity Discovery (`activity_discovery.sql`)
```sql
-- Find developers with recent activity in specific languages
SELECT
  actor.login AS username,
  COUNT(*) AS total_events,
  COUNT(DISTINCT repo.name) AS unique_repositories,
  COUNTIF(type = 'PushEvent') AS push_events,
  COUNTIF(type = 'PullRequestEvent') AS pr_events,
  COUNTIF(type = 'IssuesEvent') AS issue_events,
  ARRAY_AGG(DISTINCT repo.name LIMIT 10) AS top_repositories
FROM `githubarchive.day.{table_suffix_pattern}`
WHERE
  type IN ('PushEvent', 'PullRequestEvent', 'IssuesEvent')
  AND repo.language IN ({languages})
  AND actor.login NOT LIKE '%bot%'
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
GROUP BY username
HAVING total_events >= {min_events}
ORDER BY total_events DESC
LIMIT 1000;
```

### Template 2: Trending Detection (`trending_detection.sql`)
```sql
-- Find repositories with rapid star growth and their contributors
WITH starred_repos AS (
  SELECT
    repo.name AS repo_name,
    COUNT(*) AS recent_stars,
    MIN(created_at) AS first_star,
    MAX(created_at) AS last_star
  FROM `githubarchive.day.{table_suffix_pattern}`
  WHERE
    type = 'WatchEvent'
    AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
  GROUP BY repo_name
  HAVING recent_stars >= {min_stars}
)
SELECT
  actor.login AS username,
  STRING_AGG(DISTINCT repo.name) AS viral_repositories,
  SUM(sr.recent_stars) AS total_stars_gained,
  COUNT(DISTINCT repo.name) AS viral_repo_count
FROM `githubarchive.day.{table_suffix_pattern}` events
JOIN starred_repos sr ON events.repo.name = sr.repo_name
WHERE
  type IN ('PushEvent', 'PullRequestEvent')
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
GROUP BY username
ORDER BY total_stars_gained DESC
LIMIT 500;
```

### Template 3: Library-Specific Discovery (`library_specific.sql`)
```sql
-- Find developers working with specific libraries/frameworks
SELECT
  actor.login AS username,
  COUNT(*) AS library_events,
  COUNT(DISTINCT repo.name) AS library_repositories,
  ARRAY_AGG(DISTINCT repo.name LIMIT 5) AS matching_repos
FROM `githubarchive.day.{table_suffix_pattern}`
WHERE
  type IN ('PushEvent', 'PullRequestEvent')
  AND (
    LOWER(repo.name) LIKE '%{library_keyword}%'
    OR LOWER(repo.description) LIKE '%{library_keyword}%'
  )
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
GROUP BY username
HAVING library_events >= {min_events}
ORDER BY library_events DESC
LIMIT 1000;
```

**Quickstart Scenarios** (from spec.md acceptance scenarios):

1. **BigQuery Authentication** - Configure credentials → verify connection succeeds
2. **Activity Discovery Query** - Search Python developers with 10+ events in 30 days → verify results
3. **Cost Estimation** - Query with estimated cost $7 → verify blocked (exceeds $5 limit)
4. **Cost Tracking** - Execute query → verify actual cost logged to database
5. **Caching** - Execute same query twice → verify second query hits cache, costs $0
6. **Trending Detection** - Find developers with repos gaining 50+ stars → verify star velocity calculated
7. **Library-Specific Search** - Find pandas users → verify repository name matching
8. **Module 002 Integration** - BigQuery returns 100 usernames → verify profiles enriched via GitHub API
9. **Graceful Fallback** - Disable BigQuery credentials → verify falls back to GitHub Search API (Module 002)
10. **Merge Results** - Candidate in both BigQuery and GitHub Search → verify deduplication and data merge
11. **Activity Pattern Analysis** - Analyze contribution patterns → verify consistency_score calculated
12. **Performance** - 30-day query → verify completes within 60 seconds
13. **Error Handling** - Network timeout → verify retry logic (3 attempts)
14. **Query Optimization** - Verify partition filters applied → data scanned <100 GB

**Output**:
- data-model.md (entity definitions)
- contracts/*.json (JSON schemas)
- queries/*.sql (SQL templates)
- failing tests (test_*.py)
- quickstart.md (validation scenarios)

## Phase 2: Task Planning Approach

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md`
2. Extract tasks from contracts, SQL templates, and quickstart scenarios
3. TDD approach: tests before implementation
4. Layer-by-layer: Config → BigQuery Client → Query Builder → Activity Analyzer → Integration

**Task Categories**:

### Setup (4 tasks)
- Project structure (src/bigquery_sourcer/, tests/)
- Dependencies (google-cloud-bigquery, httpx, pydantic, redis)
- BigQuery credentials setup (service account, environment variables)
- SQL template files (config/query_templates/*.sql)

### Tests First (12 tasks)
- Contract tests (input/output/config validation)
- Unit tests (query_builder, cost_estimator, query_optimizer, query_cache, sql_template_loader)
- Integration tests (bigquery_query, activity_analysis, trending_detection, module_002_integration, cost_tracking)

### Core Implementation (12 tasks)
- Models (ActivityEnrichedCandidate, ActivityMetrics, TrendingMetrics, ContributionPatterns, BigQueryExecutionMetadata, BigQueryConfig)
- BigQuery Client (authentication, query execution, cost estimation)
- Query Builder (construct SQL from JobRequirement, parameter substitution)
- Cost Estimator (pre-execution cost calculation, budget enforcement)
- Query Optimizer (partition filters, column selection, result limits)
- Activity Analyzer (parse BigQuery results, calculate metrics)
- Trending Detector (star velocity, viral repositories)
- Query Cache (Redis integration, 24-hour TTL)
- Integration Service (merge BigQuery + Module 002 data)

### Integration (3 tasks)
- Wire all components together
- Module 002 fallback logic
- End-to-end quickstart validation

**Ordering**:
- Models before services
- Unit tests before integration tests
- Mark [P] for parallel tasks (independent test files)
- Config → BigQuery Client → Query Builder → Activity Analyzer → Integration Service

**Estimated Output**: ~30 tasks in TDD order

## Phase 3+: Future Implementation

**Phase 3**: /tasks command generates tasks.md
**Phase 4**: Execute tasks following TDD principles
**Phase 5**: Validate with quickstart.md scenarios
- Measure query performance (target: <60 seconds for 30 days)
- Verify cost tracking accuracy (compare estimated vs actual)
- Test cache hit rate (target: >50% for repeated queries)
**Phase 6**: Integration testing with Module 002 and Module 003
- Verify seamless merge of BigQuery + GitHub profile data
- Test fallback to GitHub Search API
- Validate activity signals improve ranking scores

**Phase 7**: Production Readiness
- Set up monitoring dashboards (query costs, execution times, error rates)
- Implement alerting (budget exceeded, high failure rates)
- Document BigQuery setup guide for users

## Complexity Tracking

No constitutional violations. Module follows all 5 principles:
- **Privacy-first**: Public GHArchive data only, respects GitHub ToS
- **Single source**: GHArchive BigQuery + GitHub API fallback
- **Modular**: Clear input/output contracts, standalone module
- **No AI needed**: Pure data querying and analysis
- **Transparent**: Returns cost metadata, activity source attribution

**Cost Management**:
- ✅ Pre-execution cost estimation
- ✅ Configurable cost limits ($5 default)
- ✅ Cost tracking and logging
- ✅ Query result caching (24-hour TTL)
- ✅ Budget enforcement

**Query Optimization**:
- ✅ Partition filtering (_TABLE_SUFFIX)
- ✅ Column selection (avoid SELECT *)
- ✅ Result limits (LIMIT 1000)
- ✅ Minimal data scanning (50-100 GB typical)

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed (query performance, cost accuracy)
- [ ] Phase 6: Integration testing passed
- [ ] Phase 7: Production ready

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PENDING
- [x] All research questions answered
- [x] Contracts defined
- [x] SQL templates created

**Key Milestones**:
- [ ] BigQuery authentication working
- [ ] First successful query executed
- [ ] Cost estimation accurate (within 10% of actual)
- [ ] Cache working (>50% hit rate)
- [ ] Module 002 integration working (merge activity + profile data)
- [ ] Fallback to GitHub Search API working
- [ ] Activity metrics in Ranking Engine (Module 003)

---

## Appendix: BigQuery Cost Analysis

### Cost Breakdown

**Typical Query Costs**:
- **7-day query**: 15-30 GB scanned = $0.09 - $0.19
- **30-day query**: 50-100 GB scanned = $0.31 - $0.62
- **90-day query**: 150-300 GB scanned = $0.93 - $1.85

**Factors Affecting Cost**:
- Date range (more days = more data)
- Event type filters (fewer types = less data)
- Language filters (specific languages = less data)
- Result limits (LIMIT doesn't reduce scan, but good practice)

**Cost Optimization Strategies**:
1. **Partition Filtering** - Always use `_TABLE_SUFFIX BETWEEN` for date ranges (90% cost reduction)
2. **Column Selection** - Select only needed columns (50% cost reduction vs SELECT *)
3. **Event Type Filtering** - Filter to PushEvent, PullRequestEvent only (40% reduction vs all events)
4. **Caching** - 24-hour cache avoids redundant queries (100% savings on cache hits)
5. **Result Limits** - Limit to 1000 candidates before enrichment (doesn't reduce scan, but limits downstream processing)

**Monthly Cost Projections**:
- **Light Usage** (10 queries/month): $3-6/month
- **Medium Usage** (50 queries/month): $15-30/month
- **Heavy Usage** (100 queries/month): $30-60/month
- **Free Tier**: 1 TB/month = ~500-1000 queries free

### Performance Benchmarks

**Query Execution Time**:
- **7-day query**: 10-20 seconds
- **30-day query**: 30-60 seconds
- **90-day query**: 60-90 seconds

**Factors Affecting Performance**:
- BigQuery cluster availability (varies by time of day)
- Query complexity (simple filters faster)
- Result set size (more results = slower)
- Network latency (GCP region)

**Performance Optimization**:
1. Use specific date ranges (not open-ended)
2. Apply event type filters early in WHERE clause
3. Use query timeouts (60 seconds default)
4. Cache frequently used queries

---

*Based on Constitution v1.0.0 and Module 002 (GitHub Sourcer) architecture*
*Spec approved: 2025-11-13*
*Ready for Phase 3: Task generation*
