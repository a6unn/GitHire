-- Contribution Patterns Query Template
-- Purpose: Analyze temporal contribution behaviors (consistency, peak times, streaks)
-- Cost: ~$0.50-$1.00 for 30-day scan with grouping (80-160 GB)
-- Performance: 60-90 seconds typical

-- Parameters:
-- {table_suffix_pattern}: Date range pattern
-- {start_date}: Start date in YYYYMMDD format
-- {end_date}: End date in YYYYMMDD format
-- {usernames}: Comma-separated quoted usernames (e.g., "'user1','user2','user3'")
-- {languages}: Comma-separated quoted languages (optional)

-- Note: This query is designed to run AFTER initial candidate discovery
-- It analyzes patterns for a specific list of usernames (not all developers)

SELECT
  actor.login AS username,

  -- Temporal activity breakdown
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 1) AS sunday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 2) AS monday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 3) AS tuesday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 4) AS wednesday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 5) AS thursday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 6) AS friday_events,
  COUNTIF(EXTRACT(DAYOFWEEK FROM created_at) = 7) AS saturday_events,

  -- Weekly activity timeline
  ARRAY_AGG(
    STRUCT(
      FORMAT_DATE('%Y-W%V', DATE(created_at)) AS week,
      COUNT(*) AS events
    )
    ORDER BY week
  ) AS activity_timeline,

  -- Active days count (for consistency scoring)
  COUNT(DISTINCT DATE(created_at)) AS active_days,

  -- Total events for frequency calculation
  COUNT(*) AS total_events,

  -- Date range for streak calculation
  MIN(DATE(created_at)) AS first_activity_date,
  MAX(DATE(created_at)) AS last_activity_date

FROM `githubarchive.day.{table_suffix_pattern}`

WHERE
  -- Filter to specific usernames (from initial discovery)
  actor.login IN ({usernames})

  -- Event type filters
  AND type IN ('PushEvent', 'PullRequestEvent', 'IssuesEvent', 'CreateEvent')

  -- Optional language filter
  AND (
    {languages} IS NULL
    OR repo.language IN ({languages})
  )

  -- Partition filter
  AND _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'

GROUP BY username

-- Ensure minimum activity for pattern analysis
HAVING total_events >= 5

ORDER BY username;

-- Notes on pattern classification (done in ActivityAnalyzer service):
-- - Consistent: Active on 5+ different days, low variance in daily events
-- - Bursty: High variance, activity concentrated in few days
-- - Declining: More events in first half of period than second half
-- - Growing: More events in second half of period than first half
--
-- Peak days: Days with most events (e.g., Monday, Wednesday)
-- Consistency score: active_days / total_days_in_period
-- Streak calculation: Requires day-by-day analysis in application code
