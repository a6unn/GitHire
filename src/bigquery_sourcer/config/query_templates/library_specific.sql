-- Library-Specific Activity Query Template
-- Purpose: Find developers actively working with specific libraries/frameworks
-- Cost: ~$0.40-$0.80 for 30-day scan (65-130 GB)
-- Performance: 40-70 seconds typical

-- Parameters:
-- {table_suffix_pattern}: Date range pattern
-- {start_date}: Start date in YYYYMMDD format
-- {end_date}: End date in YYYYMMDD format
-- {library_keyword}: Library name to search (e.g., "pandas", "fastapi", "react")
-- {min_events}: Minimum events with library (e.g., 5)

SELECT
  actor.login AS username,
  COUNT(*) AS library_events,
  COUNT(DISTINCT repo.name) AS library_repositories,

  -- Event type breakdown for library-specific activity
  COUNTIF(type = 'PushEvent') AS library_commits,
  COUNTIF(type = 'PullRequestEvent') AS library_prs,
  COUNTIF(type = 'CreateEvent') AS library_repos_created,

  -- Sample repositories (for validation)
  ARRAY_AGG(
    DISTINCT repo.name
    ORDER BY repo.name
    LIMIT 10
  ) AS matching_repos,

  -- First and last activity with library
  MIN(created_at) AS first_library_activity,
  MAX(created_at) AS last_library_activity

FROM `githubarchive.day.{table_suffix_pattern}`

WHERE
  -- Event type filters
  type IN ('PushEvent', 'PullRequestEvent', 'CreateEvent', 'ForkEvent')

  -- Library detection via repository name/description
  -- Case-insensitive matching for better coverage
  AND (
    -- Repository name contains library keyword
    LOWER(repo.name) LIKE CONCAT('%', LOWER('{library_keyword}'), '%')

    -- Repository description contains library keyword (if available)
    OR (
      repo.description IS NOT NULL
      AND LOWER(repo.description) LIKE CONCAT('%', LOWER('{library_keyword}'), '%')
    )
  )

  -- Partition filter (critical for cost optimization)
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'

  -- Exclude bots
  AND actor.login NOT LIKE '%bot%'
  AND actor.login NOT LIKE '%[bot]%'

GROUP BY username

-- Filter by minimum library-specific activity
HAVING library_events >= {min_events}

-- Sort by most active with library
ORDER BY library_events DESC, library_repositories DESC

-- Limit results
LIMIT 1000;
