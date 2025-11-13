-- Activity Discovery Query Template
-- Purpose: Find developers with recent activity in specific programming languages
-- Cost: ~$0.31-$0.62 for 30-day scan (50-100 GB)
-- Performance: 30-60 seconds typical

-- Parameters:
-- {table_suffix_pattern}: Date range pattern (e.g., "2025*" for all of 2025)
-- {languages}: Comma-separated quoted languages (e.g., "'Python','JavaScript','Go'")
-- {start_date}: Start date in YYYYMMDD format (e.g., "20250101")
-- {end_date}: End date in YYYYMMDD format (e.g., "20250131")
-- {min_events}: Minimum event count threshold (e.g., 10)

SELECT
  actor.login AS username,
  COUNT(*) AS total_events,
  COUNT(DISTINCT repo.name) AS unique_repositories,
  COUNTIF(type = 'PushEvent') AS push_events,
  COUNTIF(type = 'PullRequestEvent') AS pr_events,
  COUNTIF(type = 'IssuesEvent') AS issue_events,
  COUNTIF(type = 'IssueCommentEvent') AS comment_events,
  ARRAY_AGG(DISTINCT repo.name ORDER BY repo.name LIMIT 10) AS top_repositories,
  MIN(created_at) AS first_event_date,
  MAX(created_at) AS last_event_date
FROM `githubarchive.day.{table_suffix_pattern}`
WHERE
  -- Event type filters (reduce scan by 40%)
  type IN ('PushEvent', 'PullRequestEvent', 'IssuesEvent', 'IssueCommentEvent')

  -- Language filter (if specified)
  AND (
    {languages} IS NULL
    OR repo.language IN ({languages})
  )

  -- Exclude bots
  AND actor.login NOT LIKE '%bot%'
  AND actor.login NOT LIKE '%[bot]%'

  -- Partition filter (critical for cost optimization - 90% reduction)
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'

GROUP BY username

-- Filter by minimum activity threshold
HAVING total_events >= {min_events}

-- Sort by most active developers
ORDER BY total_events DESC

-- Limit results before enrichment (prevent overwhelming GitHub API)
LIMIT 1000;
