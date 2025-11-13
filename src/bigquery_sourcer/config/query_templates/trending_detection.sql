-- Trending Detection Query Template
-- Purpose: Find repositories with rapid star growth and identify their contributors
-- Cost: ~$0.50-$1.00 for 90-day scan (80-160 GB)
-- Performance: 60-90 seconds typical

-- Parameters:
-- {table_suffix_pattern}: Date range pattern (e.g., "2025*")
-- {start_date}: Start date in YYYYMMDD format
-- {end_date}: End date in YYYYMMDD format
-- {min_stars}: Minimum stars gained in period (e.g., 50)
-- {languages}: Comma-separated quoted languages (optional)

-- Step 1: Identify repositories with rapid star growth
WITH starred_repos AS (
  SELECT
    repo.name AS repo_name,
    repo.language AS repo_language,
    COUNT(*) AS recent_stars,
    MIN(created_at) AS first_star,
    MAX(created_at) AS last_star,
    -- Calculate star velocity (stars per day)
    COUNT(*) / GREATEST(DATE_DIFF(
      MAX(DATE(created_at)),
      MIN(DATE(created_at)),
      DAY
    ), 1) AS star_velocity
  FROM `githubarchive.day.{table_suffix_pattern}`
  WHERE
    type = 'WatchEvent'
    AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
    -- Optional language filter
    AND (
      {languages} IS NULL
      OR repo.language IN ({languages})
    )
  GROUP BY repo_name, repo_language

  -- Filter for viral repositories (50+ stars in period)
  HAVING recent_stars >= {min_stars}
),

-- Step 2: Find contributors to these viral repositories
viral_contributors AS (
  SELECT
    events.actor.login AS username,
    events.repo.name AS repo_name,
    COUNT(*) AS contribution_count,
    sr.recent_stars,
    sr.star_velocity
  FROM `githubarchive.day.{table_suffix_pattern}` events
  INNER JOIN starred_repos sr
    ON events.repo.name = sr.repo_name
  WHERE
    -- Focus on meaningful contributions
    type IN ('PushEvent', 'PullRequestEvent')
    AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
    -- Exclude bots
    AND events.actor.login NOT LIKE '%bot%'
  GROUP BY
    username,
    repo_name,
    sr.recent_stars,
    sr.star_velocity
)

-- Step 3: Aggregate by contributor
SELECT
  username,
  -- Trending metrics
  ARRAY_AGG(
    STRUCT(
      repo_name AS repo,
      recent_stars AS stars,
      CAST(star_velocity AS FLOAT64) AS stars_per_day,
      contribution_count AS events
    )
    ORDER BY recent_stars DESC
    LIMIT 5
  ) AS viral_repositories,
  SUM(recent_stars) AS total_stars_gained,
  SUM(contribution_count) AS total_contributions,
  COUNT(DISTINCT repo_name) AS viral_repo_count,
  AVG(star_velocity) AS avg_star_velocity
FROM viral_contributors
GROUP BY username

-- Prioritize developers with multiple viral projects or high contributions
ORDER BY viral_repo_count DESC, total_stars_gained DESC

-- Limit to top trending developers
LIMIT 500;
