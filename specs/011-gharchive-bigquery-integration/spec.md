# Feature Specification: GHArchive BigQuery Integration Module

**Feature Branch**: `011-gharchive-bigquery-integration`
**Created**: 2025-11-13
**Status**: Draft
**Input**: JobRequirement from JD Parser (Module 001) and configuration for BigQuery access

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts ✓
   → Input: JobRequirement (from Module 001)
   → Action: Query GHArchive BigQuery for real-time GitHub activity
   → Output: Activity-enriched candidate profiles with contribution patterns
   → Constraints: BigQuery costs, query optimization, privacy compliance
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

The GHArchive BigQuery Integration Module provides access to historical and real-time GitHub activity data to discover candidates based on their actual contribution patterns, not just profile information. It should:

1. **Query** GHArchive's BigQuery dataset for developers who recently contributed to specific technologies
2. **Analyze** real-time GitHub events (commits, PRs, issues, stars) from the last 7-90 days
3. **Discover** trending developers gaining community recognition
4. **Identify** developers actively working with specific frameworks/libraries
5. **Enrich** candidate profiles with activity metrics and contribution patterns
6. **Integrate** seamlessly with existing GitHub Search API sourcing (Module 002)

The module operates as an enhanced candidate discovery layer that complements traditional GitHub profile search with activity-based intelligence.

### Acceptance Scenarios

#### Core BigQuery Integration

1. **Given** a JobRequirement with required_skills=["Python", "FastAPI"], **When** querying GHArchive, **Then** it returns developers who committed to FastAPI-related repositories in the last 30 days

2. **Given** a JobRequirement with required_skills=["React", "TypeScript"], **When** querying GHArchive, **Then** it identifies developers who opened PRs to React repositories in the last 90 days

3. **Given** BigQuery credentials are configured, **When** initializing the module, **Then** it validates BigQuery access and returns connection status

4. **Given** BigQuery credentials are not configured, **When** the module is invoked, **Then** it gracefully falls back to GitHub Search API (Module 002) without errors

5. **Given** a BigQuery query execution, **When** processing, **Then** the module tracks and reports query costs in dollars

6. **Given** multiple similar queries within 24 hours, **When** executing searches, **Then** it uses cached results to minimize BigQuery costs

#### Real-Time Activity Detection

7. **Given** a JobRequirement requesting "active contributors", **When** querying GHArchive, **Then** it filters developers with 10+ events in the last 30 days

8. **Given** a search for Python developers, **When** analyzing activity, **Then** it discovers developers with recent PushEvents to Python repositories

9. **Given** a JobRequirement, **When** querying activity data, **Then** it identifies developers' most active repositories and contribution frequency

10. **Given** a candidate's GitHub username from BigQuery, **When** enriching the profile, **Then** it includes event counts by type (PushEvent, PullRequestEvent, IssuesEvent)

#### Trending Developer Discovery

11. **Given** a JobRequirement with required_skills=["Machine Learning"], **When** querying trending patterns, **Then** it identifies developers whose ML repositories gained 50+ stars in the last 90 days

12. **Given** star growth tracking, **When** analyzing WatchEvents, **Then** it calculates star velocity (stars per day) for candidate repositories

13. **Given** a developer with viral repository activity, **When** ranking candidates, **Then** trending developers receive priority ranking boost

14. **Given** trending analysis, **When** presenting results, **Then** it shows which repositories are gaining traction and why

#### Library/Framework-Specific Detection

15. **Given** a JobRequirement with required_skills=["pandas", "numpy"], **When** querying GHArchive, **Then** it finds developers who committed to repositories using these specific libraries

16. **Given** a JobRequirement with required_skills=["Django"], **When** analyzing commits, **Then** it identifies developers whose recent commits modified Django-related files

17. **Given** library-specific search, **When** querying repository names, **Then** it matches repositories with keywords like "django-", "flask-", "fastapi-" in their names

18. **Given** package dependency analysis, **When** available in GHArchive data, **Then** it detects library usage from requirements.txt, package.json mentions in commits

#### Location-Based Activity Filtering

19. **Given** a JobRequirement with location="San Francisco", **When** querying GHArchive, **Then** it filters candidates by location after retrieving activity data

20. **Given** location-based filtering, **When** combining with activity data, **Then** it prioritizes local candidates with high activity scores

#### Performance and Cost Optimization

21. **Given** a BigQuery query, **When** executing, **Then** it completes within 30-60 seconds for queries scanning 7-30 days of data

22. **Given** query execution, **When** scanning GHArchive data, **Then** it limits scans to specific date ranges (e.g., last 30 days) to control costs

23. **Given** a query result cache hit, **When** reusing cached data, **Then** it returns results in under 2 seconds without BigQuery charges

24. **Given** estimated query costs exceed $5, **When** executing, **Then** it warns the user and requests confirmation before proceeding

25. **Given** query optimization, **When** constructing BigQuery SQL, **Then** it uses partition filters (_TABLE_SUFFIX) to minimize data scanned

#### Integration with GitHub Sourcer (Module 002)

26. **Given** BigQuery returns 500 candidate usernames, **When** enriching profiles, **Then** it passes candidates to Module 002 for full profile enrichment

27. **Given** both BigQuery and GitHub Search API results, **When** merging candidates, **Then** it deduplicates by username and combines data sources

28. **Given** a candidate found in both sources, **When** enriching, **Then** it merges activity data from BigQuery with profile data from GitHub API

29. **Given** Module 002 enrichment failure for BigQuery candidates, **When** handling errors, **Then** it returns partial results with activity data only

#### Contribution Pattern Analysis

30. **Given** a candidate's event history, **When** analyzing patterns, **Then** it identifies peak contribution days/times and consistency

31. **Given** contribution frequency data, **When** calculating metrics, **Then** it provides average events per week and contribution streak length

32. **Given** event type distribution, **When** analyzing, **Then** it shows percentage breakdown (commits 60%, PRs 30%, issues 10%)

33. **Given** repository diversity, **When** analyzing contributions, **Then** it counts unique repositories contributed to in the time period

#### Advanced Discovery Queries

34. **Given** a JobRequirement with experience_years >= 5, **When** querying GHArchive, **Then** it filters developers with 1000+ total contribution events across all time

35. **Given** a search for open source maintainers, **When** analyzing PullRequestEvent merges, **Then** it identifies developers who merged 20+ PRs in their repositories

36. **Given** a search for code reviewers, **When** analyzing IssueCommentEvent on PRs, **Then** it finds developers actively reviewing others' code

37. **Given** a search for early adopters, **When** analyzing repository creation dates, **Then** it identifies developers who created repositories with new technologies within 6 months of release

#### Data Freshness

38. **Given** GHArchive updates hourly, **When** querying recent activity, **Then** it includes events up to 1 hour old

39. **Given** a JobRequirement requesting "currently active" developers, **When** querying, **Then** it filters to events from the last 7 days only

40. **Given** stale cached results (>24 hours), **When** executing a query, **Then** it automatically refreshes from BigQuery

### Edge Cases

- **What happens when BigQuery quotas are exceeded?**
  - Return cached results if available, fall back to GitHub Search API, notify user of quota limit

- **What happens when GHArchive data is incomplete for a specific date?**
  - Log the gap, continue with available data, include data completeness metadata in results

- **What happens when a query would cost more than $10?**
  - Block execution, show cost estimate, require explicit user confirmation or query refinement

- **What happens when no candidates match activity criteria?**
  - Return empty result set, suggest broadening criteria (e.g., extend time range from 30 to 90 days)

- **What happens when a candidate's GitHub profile is deleted after BigQuery discovery?**
  - Module 002 enrichment fails, return candidate with activity data only, mark profile as unavailable

- **What happens when BigQuery returns 10,000+ candidate usernames?**
  - Apply ranking/filtering before enrichment (top 500 by activity score), avoid overloading GitHub API

- **What happens when querying for very common activities (e.g., all Python commits)?**
  - Return warning about broad query, suggest adding filters (location, star count, PR count)

- **What happens when GHArchive schema changes?**
  - Query validation fails, log error, fall back to GitHub Search API, alert maintainers

- **What happens when network connection to BigQuery fails?**
  - Use exponential backoff with 3 retries, then fall back to cached results or GitHub Search API

- **What happens when a user has no BigQuery project configured?**
  - Detect missing configuration, provide setup instructions, skip BigQuery integration gracefully

- **What happens when combining BigQuery results with GitHub Search API results?**
  - Merge by username, prioritize BigQuery activity data, supplement with GitHub profile data

- **What happens when a candidate appears in GHArchive but has privacy-protected profile?**
  - Respect privacy settings, exclude from results if profile enrichment fails due to privacy

- **What happens when querying historical data (>6 months old)?**
  - Allow query but warn about increased costs, suggest using monthly tables instead of daily

- **What happens when a developer's activity is primarily in private repositories?**
  - GHArchive only captures public events, activity metrics reflect public contributions only

---

## Requirements *(mandatory)*

### Functional Requirements

#### Configuration and Initialization

- **FR-001**: Module MUST support optional configuration for BigQuery credentials (GCP project ID, service account key)
- **FR-002**: Module MUST validate BigQuery access on initialization and report connection status
- **FR-003**: Module MUST gracefully disable BigQuery features if credentials are not configured
- **FR-004**: Module MUST allow configuration of query cost limits (default: $5 per query)
- **FR-005**: Module MUST allow configuration of date ranges for activity queries (default: 30 days)

#### GHArchive BigQuery Querying

- **FR-006**: Module MUST query GHArchive BigQuery dataset (githubarchive.day.YYYYMMDD tables)
- **FR-007**: Module MUST filter events by type (PushEvent, PullRequestEvent, IssuesEvent, WatchEvent, etc.)
- **FR-008**: Module MUST filter events by programming language and technology keywords
- **FR-009**: Module MUST support date range filtering (last 7, 30, 90 days)
- **FR-010**: Module MUST extract GitHub usernames from event actor.login field
- **FR-011**: Module MUST deduplicate usernames across multiple events
- **FR-012**: Module MUST calculate activity metrics per candidate (event count, event types, repository diversity)

#### Activity Pattern Analysis

- **FR-013**: Module MUST count total events per candidate in the specified time period
- **FR-014**: Module MUST breakdown event types by percentage (PushEvent, PullRequestEvent, etc.)
- **FR-015**: Module MUST identify candidate's most active repositories
- **FR-016**: Module MUST calculate contribution frequency (events per week)
- **FR-017**: Module MUST detect contribution patterns (consistent, bursty, declining)
- **FR-018**: Module SHOULD identify contribution time patterns (peak days/hours)

#### Trending Developer Detection

- **FR-019**: Module MUST track WatchEvent (stars) for candidate repositories
- **FR-020**: Module MUST calculate star velocity (stars gained per day/week)
- **FR-021**: Module MUST identify repositories with rapid star growth (50+ stars in 90 days)
- **FR-022**: Module SHOULD identify early adopters (contributions to new technologies within 6 months of release)

#### Library/Framework-Specific Detection

- **FR-023**: Module MUST filter commits to repositories with specific technologies in name or description
- **FR-024**: Module MUST detect library usage from repository names (e.g., "django-blog", "fastapi-starter")
- **FR-025**: Module SHOULD analyze commit payloads for file paths indicating framework usage (e.g., "requirements.txt", "package.json")
- **FR-026**: Module MUST support querying for multiple libraries simultaneously (e.g., pandas AND numpy)

#### Cost Management

- **FR-027**: Module MUST estimate query costs before execution using BigQuery API
- **FR-028**: Module MUST track actual query costs and log them for billing purposes
- **FR-029**: Module MUST block query execution if estimated cost exceeds configured limit
- **FR-030**: Module MUST provide cost breakdowns (data scanned GB, cost per GB)
- **FR-031**: Module MUST cache query results for 24 hours to avoid redundant charges

#### Performance

- **FR-032**: Module MUST complete BigQuery queries within 60 seconds for 30-day date ranges
- **FR-033**: Module MUST use partition filters to minimize data scanned
- **FR-034**: Module MUST limit result sets to top 1000 candidates by activity score before enrichment
- **FR-035**: Module SHOULD use query optimization (avoiding SELECT *, using specific columns)

#### Integration with Module 002 (GitHub Sourcer)

- **FR-036**: Module MUST pass discovered candidate usernames to Module 002 for profile enrichment
- **FR-037**: Module MUST merge BigQuery activity data with GitHub profile data
- **FR-038**: Module MUST deduplicate candidates found in both BigQuery and GitHub Search API
- **FR-039**: Module MUST support fallback to GitHub Search API if BigQuery fails
- **FR-040**: Module MUST enrich candidates with activity metrics before passing to Module 003 (Ranking Engine)

#### Output Format

- **FR-041**: Module MUST return list of ActivityEnrichedCandidate objects
- **FR-042**: Each ActivityEnrichedCandidate MUST include: github_username, total_events, event_breakdown, top_repositories, contribution_frequency
- **FR-043**: Module MUST return query metadata: data_source="bigquery", query_cost_usd, data_scanned_gb, query_duration_ms, date_range
- **FR-044**: Module MUST include trending metrics if available: star_velocity, viral_repositories, recent_stars
- **FR-045**: Module MUST return empty list (not error) if no candidates match activity criteria

#### Error Handling

- **FR-046**: Module MUST handle BigQuery authentication errors and provide clear setup instructions
- **FR-047**: Module MUST handle BigQuery quota exceeded errors and suggest cost optimization
- **FR-048**: Module MUST handle network failures with retry logic (3 attempts, exponential backoff)
- **FR-049**: Module MUST fall back to cached results if BigQuery is temporarily unavailable
- **FR-050**: Module MUST fall back to GitHub Search API if BigQuery integration fails

#### Data Privacy and Compliance

- **FR-051**: Module MUST only query public GitHub events from GHArchive
- **FR-052**: Module MUST respect GitHub's Terms of Service regarding bulk data access
- **FR-053**: Module MUST not circumvent rate limits or privacy protections
- **FR-054**: Module MUST include data source attribution (GHArchive) in all results
- **FR-055**: Module MUST support GDPR-compliant data retention for activity metrics

---

### Key Entities

#### ActivityEnrichedCandidate (Output)
- Represents a GitHub developer discovered via activity analysis
- Attributes:
  - github_username (unique identifier)
  - activity_metrics (ActivityMetrics object)
  - trending_metrics (TrendingMetrics object, optional)
  - contribution_patterns (ContributionPatterns object)
  - discovered_via (string: "bigquery", "github_search", or "both")
  - activity_score (float 0-100, calculated from event frequency and quality)
  - data_freshness (datetime, when GHArchive data was last updated)
- Relationships: Extends Candidate from Module 002 with activity enrichment
- User Value: Enables discovery of actively contributing developers beyond static profile data

#### ActivityMetrics (Embedded)
- Represents quantitative activity measurements
- Attributes:
  - total_events (int, total GitHub events in time period)
  - event_breakdown (dict, percentage by type: {"PushEvent": 65%, "PullRequestEvent": 25%})
  - unique_repositories (int, number of different repos contributed to)
  - contribution_frequency (float, average events per week)
  - active_days (int, number of days with at least one event)
  - consistency_score (float 0-1, measures regular vs bursty contributions)
  - top_repositories (list of repo names with event counts)
- Relationships: Embedded in ActivityEnrichedCandidate
- User Value: Quantifies developer's activity level and engagement

#### TrendingMetrics (Embedded, Optional)
- Represents trending/viral activity indicators
- Attributes:
  - star_velocity (float, stars gained per day)
  - recent_stars (int, stars gained in time period)
  - viral_repositories (list of repos with 50+ stars in 90 days)
  - follower_growth (int, new followers in time period, if available)
  - early_adopter_signals (list of new technologies adopted)
- Relationships: Embedded in ActivityEnrichedCandidate
- User Value: Identifies rising talent before they become hard to recruit

#### ContributionPatterns (Embedded)
- Represents temporal contribution behaviors
- Attributes:
  - pattern_type (enum: "consistent", "bursty", "declining", "growing")
  - peak_days (list of weekdays with most activity)
  - peak_hours (list of hours with most activity, if available)
  - longest_streak (int, consecutive days with contributions)
  - current_streak (int, ongoing consecutive days)
  - activity_timeline (list of event counts per week)
- Relationships: Embedded in ActivityEnrichedCandidate
- User Value: Helps assess developer engagement and work patterns

#### BigQueryExecutionMetadata (Output Metadata)
- Represents BigQuery query execution details
- Attributes:
  - query_cost_usd (float, actual cost of query execution)
  - estimated_cost_usd (float, pre-execution estimate)
  - data_scanned_gb (float, gigabytes of data scanned)
  - query_duration_ms (int, execution time in milliseconds)
  - date_range (tuple, start_date and end_date of queried data)
  - cache_hit (bool, whether results came from cache)
  - candidates_found (int, total usernames discovered)
  - candidates_returned (int, after filtering and deduplication)
  - table_suffix_pattern (string, which GHArchive tables were queried)
- Relationships: Returned alongside ActivityEnrichedCandidate list
- User Value: Transparency in costs and query performance

#### BigQueryConfig (Configuration)
- Represents BigQuery connection and query settings
- Attributes:
  - gcp_project_id (string, Google Cloud Project ID)
  - service_account_key_path (string, path to JSON key file)
  - max_query_cost_usd (float, maximum allowed cost per query, default: $5)
  - default_date_range_days (int, default lookback period, default: 30)
  - cache_ttl_hours (int, cache duration, default: 24)
  - enable_trending_detection (bool, calculate star velocity, default: true)
  - max_candidates_before_enrichment (int, limit before GitHub API enrichment, default: 500)
- Relationships: Used to initialize BigQuery client
- User Value: Controls costs and behavior without code changes

---

## Dependencies

### Input Dependencies
- **Module 001 (JD Parser)**: Provides JobRequirement JSON as input
  - Required fields: required_skills (list), role (string or null)
  - Optional fields: preferred_skills, location_preferences, experience_years, seniority_level

### External Dependencies
- **Google BigQuery API**: Access to GHArchive public dataset
  - Dataset: `githubarchive.day.YYYYMMDD` (daily tables) and `githubarchive.month.YYYYMM` (monthly tables)
  - Cost: $6.25 per TB scanned (as of 2025, subject to change)
  - Free tier: 1 TB query per month
  - Query time: 10-60 seconds depending on date range and filters
  - Rate limits: 100 concurrent queries per project
  - Authentication: Service account with BigQuery User role

- **GHArchive Dataset Structure**: Public GitHub event archive
  - Tables: Daily (2015-present), Monthly (2011-2015), Historical (2011-2015)
  - Event types: PushEvent, PullRequestEvent, IssuesEvent, WatchEvent, ForkEvent, CreateEvent, etc.
  - Fields: actor.login, repo.name, repo.language, type, created_at, payload
  - Update frequency: Hourly (last hour's events added)
  - Data retention: Indefinite (all historical data available)

- **Module 002 (GitHub Sourcer)**: Enriches BigQuery-discovered candidates
  - Input: List of github_usernames from BigQuery
  - Output: Full Candidate profiles with repositories, skills, location
  - Fallback: Used as primary source if BigQuery unavailable

### Output Consumers
- **Module 003 (Ranking Engine)**: Ranks ActivityEnrichedCandidate with activity signals
  - Activity score contributes to overall ranking
  - Trending developers may receive priority boost
- **Module 005 (Backend API)**: Stores activity metrics in database
- **Frontend Application**: Displays activity patterns and trending indicators

---

## Performance Requirements

- **PR-001**: BigQuery queries must complete within 60 seconds for 30-day date ranges
- **PR-002**: Module must complete within 90 seconds for 90-day date ranges
- **PR-003**: Cache hits must return results in under 2 seconds
- **PR-004**: Module must limit data scanned to under 100 GB per query to control costs
- **PR-005**: Module must support concurrent query execution for multiple job requirements
- **PR-006**: Module must batch candidate enrichment to avoid overwhelming GitHub API (max 500 candidates)

---

## Constitutional Rules *(governance)*

### CR-001: No Hardcoded BigQuery SQL Queries
**Rule**: All BigQuery SQL query templates MUST be configurable via external template files or query builders.

**Rationale**: Query patterns may need optimization over time; hardcoding SQL creates maintenance burden and reduces flexibility.

**Applies To**:
- Base query templates for activity detection
- Filter clauses for skill/language matching
- Aggregation logic for activity metrics
- Date range partition filters

**Examples**:
- ❌ BAD: SQL query string embedded in Python code
- ✅ GOOD: SQL template loaded from `config/bigquery_templates/activity_discovery.sql`
- ❌ BAD: Hardcoded event type filters in WHERE clause
- ✅ GOOD: Event types loaded from `config.enabled_event_types`

### CR-002: Cost Transparency and Control
**Rule**: All query cost estimates and actuals MUST be logged, reported to users, and subject to configurable limits.

**Rationale**: BigQuery costs can escalate quickly; users need visibility and control to prevent unexpected bills.

**Applies To**:
- Pre-execution cost estimation
- Post-execution actual cost logging
- Per-user or per-project cost budgets
- Cost alerts and warnings

**Examples**:
- ✅ REQUIRED: Show "Estimated cost: $2.35" before query execution
- ✅ REQUIRED: Log all queries with timestamps and costs to database
- ✅ REQUIRED: Block execution if `estimated_cost > config.max_query_cost`
- ✅ REQUIRED: Monthly cost aggregation and reporting dashboard

### CR-003: Graceful Degradation to GitHub Search API
**Rule**: Module MUST seamlessly fall back to GitHub Search API (Module 002) if BigQuery is unavailable, misconfigured, or quota-limited.

**Rationale**: BigQuery is an enhancement, not a requirement; core functionality must work without it.

**Applies To**:
- Missing BigQuery credentials
- BigQuery authentication failures
- Query quota exhaustion
- Network failures
- GHArchive data unavailability

**Examples**:
- ✅ REQUIRED: Detect missing `GCP_PROJECT_ID`, skip BigQuery silently
- ✅ REQUIRED: On BigQuery error, log warning and call Module 002
- ✅ REQUIRED: Return candidates with `discovered_via: "github_search"` on fallback
- ❌ BAD: Crash or return error if BigQuery fails

### CR-004: Configurable Activity Thresholds
**Rule**: All activity-based filtering thresholds (minimum events, date ranges, trending metrics) MUST be configurable externally.

**Rationale**: Optimal thresholds vary by job seniority, role, and market conditions; configuration enables experimentation.

**Applies To**:
- Minimum event count to consider a candidate
- Date range for "recent activity" (7, 30, 90 days)
- Star velocity threshold for "trending developer"
- Contribution consistency score calculation
- Repository diversity thresholds

**Examples**:
- ❌ BAD: `if total_events > 100` (hardcoded threshold)
- ✅ GOOD: `if total_events > config.min_activity_events` (configurable)
- ❌ BAD: Date range fixed to 30 days
- ✅ GOOD: `date_range = config.activity_lookback_days` (configurable)

### CR-005: GHArchive Data Attribution
**Rule**: All output and UI displays MUST clearly attribute data to GHArchive and include appropriate disclaimers.

**Rationale**: Legal and ethical obligation to credit data source; GHArchive requires attribution per their terms.

**Applies To**:
- API response metadata
- Frontend candidate cards
- Exported reports
- Documentation

**Examples**:
- ✅ REQUIRED: Include `"data_source": "GHArchive (gharchive.org)"` in API response
- ✅ REQUIRED: Display "Activity data from GHArchive" in UI
- ✅ REQUIRED: Include GHArchive attribution in PDF exports
- ✅ REQUIRED: Link to gharchive.org in documentation

### CR-006: Query Optimization by Default
**Rule**: All BigQuery queries MUST use partition filters, column selection, and result limits to minimize costs.

**Rationale**: Inefficient queries can cost hundreds of dollars; optimization must be built-in, not optional.

**Applies To**:
- Using `_TABLE_SUFFIX` for date range filtering
- Selecting specific columns instead of `SELECT *`
- Using `LIMIT` clauses to cap result sets
- Avoiding full table scans

**Examples**:
- ✅ REQUIRED: `WHERE _TABLE_SUFFIX BETWEEN '20250101' AND '20250131'`
- ✅ REQUIRED: `SELECT actor.login, type, repo.name` (not `SELECT *`)
- ✅ REQUIRED: `LIMIT 1000` on all queries
- ❌ BAD: Scanning entire `githubarchive.year.2025` table without date filter

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (query time < 60s, cost < $5)
- [x] Scope is clearly bounded (discovery and activity enrichment only)
- [x] Dependencies and assumptions identified

### Cost & Performance
- [x] Cost management requirements specified
- [x] Performance targets defined
- [x] Query optimization requirements included
- [x] Fallback strategies documented

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted (input, action, output, constraints)
- [x] Ambiguities marked and resolved
- [x] User scenarios defined (40 acceptance scenarios)
- [x] Requirements generated (55 functional requirements)
- [x] Entities identified (6 entities)
- [x] Review checklist passed

---

## Clarifications Resolved

1. **Query Cost Limit**: Default $5 per query, configurable
2. **Date Range**: Default 30 days, configurable (7, 30, 90 days)
3. **Cache Duration**: 24 hours for query results
4. **Fallback Strategy**: Automatic fallback to GitHub Search API (Module 002)
5. **Result Limit**: Top 1000 candidates by activity score before enrichment
6. **Integration Mode**: Complements (not replaces) GitHub Search API

---

## Success Metrics

### Discovery Effectiveness
- **Target**: Discover 30-50% more qualified candidates vs GitHub Search alone
- **Metric**: Unique candidates found via BigQuery activity filters
- **Measurement**: A/B test with and without BigQuery integration

### Activity Signal Value
- **Target**: Candidates with activity signals rank 20%+ higher on average
- **Metric**: Average ranking score for BigQuery-discovered vs search-discovered candidates
- **Measurement**: Compare Module 003 ranking scores by discovery source

### Cost Efficiency
- **Target**: Average query cost under $2 per job search
- **Metric**: Total BigQuery costs / number of job searches
- **Measurement**: Monthly cost tracking and dashboard

### Performance
- **Target**: 95% of queries complete within 60 seconds
- **Metric**: Query duration percentile distribution
- **Measurement**: Execution time logging and monitoring

### User Adoption
- **Target**: 70% of users enable BigQuery after trial
- **Metric**: Percentage of projects with BigQuery enabled
- **Measurement**: Feature flag tracking in database

---

## Next Steps

1. **Create plan.md** → Research BigQuery best practices, design query templates, define data models
2. **Create tasks.md** → TDD task breakdown for implementation
3. **Set up BigQuery sandbox** → Test environment for query development and cost estimation
4. **Build Module 011** → Following constitutional principles and cost optimization
5. **Integration testing** → Validate with Module 002 (GitHub Sourcer) and Module 003 (Ranking Engine)
6. **Cost monitoring** → Implement dashboards for query cost tracking

---

## Appendix: GHArchive Dataset Schema Reference

### Event Types
- **PushEvent**: Code commits pushed to repositories
- **PullRequestEvent**: Pull requests opened, closed, or merged
- **IssuesEvent**: Issues opened, closed, or commented on
- **WatchEvent**: Repository stars (called "watch" in GitHub API)
- **ForkEvent**: Repository forks
- **CreateEvent**: Repository, branch, or tag creation
- **IssueCommentEvent**: Comments on issues or pull requests
- **DeleteEvent**: Branch or tag deletion

### Key Fields
```json
{
  "type": "PushEvent",
  "actor": {
    "login": "username",
    "id": 12345,
    "avatar_url": "https://..."
  },
  "repo": {
    "name": "owner/repo",
    "url": "https://api.github.com/repos/owner/repo"
  },
  "payload": {
    "commits": [...],
    "size": 3,
    "ref": "refs/heads/main"
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Table Naming Convention
- Daily: `githubarchive.day.YYYYMMDD` (e.g., `githubarchive.day.20250115`)
- Monthly: `githubarchive.month.YYYYMM` (e.g., `githubarchive.month.202501`)
- Wildcard: `githubarchive.day.2025*` (all days in 2025)

### Cost Estimation Formula
```
Cost = (Data Scanned in GB) × $6.25
```

Example: Querying 30 days of data typically scans 50-100 GB = $0.31 - $0.62 per query

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Ready for Planning**: ✅ Yes
