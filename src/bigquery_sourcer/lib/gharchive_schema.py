"""
GHArchive Schema Reference

Defines event types, field structures, and parsing utilities for GHArchive BigQuery dataset.

GHArchive captures all public GitHub events and stores them in BigQuery tables:
- Daily tables: githubarchive.day.YYYYMMDD (e.g., githubarchive.day.20250113)
- Monthly tables: githubarchive.month.YYYYMM (historical, pre-2015)
- Update frequency: Hourly (new events added every hour)

Documentation: https://www.gharchive.org/
BigQuery Dataset: https://console.cloud.google.com/bigquery?p=githubarchive
"""

from enum import Enum
from typing import TypedDict, Optional, List, Dict, Any


class EventType(str, Enum):
    """
    GitHub event types captured by GHArchive.

    Reference: https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
    """

    # Code Events
    PUSH_EVENT = "PushEvent"  # Commits pushed to repository
    CREATE_EVENT = "CreateEvent"  # Repository, branch, or tag created
    DELETE_EVENT = "DeleteEvent"  # Branch or tag deleted

    # Pull Request Events
    PULL_REQUEST_EVENT = "PullRequestEvent"  # PR opened, closed, merged, etc.
    PULL_REQUEST_REVIEW_EVENT = "PullRequestReviewEvent"  # PR reviewed
    PULL_REQUEST_REVIEW_COMMENT_EVENT = "PullRequestReviewCommentEvent"  # Comment on PR review

    # Issue Events
    ISSUES_EVENT = "IssuesEvent"  # Issue opened, closed, etc.
    ISSUE_COMMENT_EVENT = "IssueCommentEvent"  # Comment on issue or PR

    # Social Events
    WATCH_EVENT = "WatchEvent"  # Repository starred (called "watch" in API)
    FORK_EVENT = "ForkEvent"  # Repository forked
    FOLLOW_EVENT = "FollowEvent"  # DEPRECATED: No longer tracked

    # Repository Events
    PUBLIC_EVENT = "PublicEvent"  # Private repository made public
    MEMBER_EVENT = "MemberEvent"  # Collaborator added to repository
    MEMBERSHIP_EVENT = "MembershipEvent"  # Team membership changed

    # Release Events
    RELEASE_EVENT = "ReleaseEvent"  # Release published

    # Other Events
    GOLLUM_EVENT = "GollumEvent"  # Wiki page created or updated
    COMMIT_COMMENT_EVENT = "CommitCommentEvent"  # Comment on a commit


class GHArchiveActor(TypedDict):
    """Actor (user) who triggered the event."""

    id: int  # GitHub user ID
    login: str  # GitHub username
    display_login: Optional[str]  # Display name variant
    gravatar_id: str  # Gravatar ID
    url: str  # API URL for user
    avatar_url: str  # Avatar image URL


class GHArchiveRepo(TypedDict):
    """Repository where event occurred."""

    id: int  # GitHub repository ID
    name: str  # Full repository name (owner/repo)
    url: str  # API URL for repository
    language: Optional[str]  # Primary programming language
    description: Optional[str]  # Repository description


class GHArchiveOrg(TypedDict):
    """Organization (if repository is under an org)."""

    id: int  # GitHub organization ID
    login: str  # Organization name
    gravatar_id: str  # Gravatar ID
    url: str  # API URL for organization
    avatar_url: str  # Avatar image URL


class GHArchiveEvent(TypedDict):
    """
    Base structure for all GHArchive events.

    Common fields across all event types.
    """

    id: str  # Unique event ID
    type: str  # Event type (see EventType enum)
    actor: GHArchiveActor  # User who triggered event
    repo: GHArchiveRepo  # Repository where event occurred
    org: Optional[GHArchiveOrg]  # Organization (if applicable)
    payload: Dict[str, Any]  # Event-specific payload (varies by type)
    public: bool  # Always true (GHArchive only captures public events)
    created_at: str  # ISO 8601 timestamp (e.g., "2025-01-13T10:30:00Z")


class PushEventPayload(TypedDict):
    """Payload structure for PushEvent."""

    push_id: int  # Unique push ID
    size: int  # Number of commits in push
    distinct_size: int  # Number of distinct commits
    ref: str  # Branch ref (e.g., "refs/heads/main")
    head: str  # Commit SHA after push
    before: str  # Commit SHA before push
    commits: List[Dict[str, Any]]  # List of commit objects


class PullRequestEventPayload(TypedDict):
    """Payload structure for PullRequestEvent."""

    action: str  # Action: opened, closed, reopened, synchronize, etc.
    number: int  # Pull request number
    pull_request: Dict[str, Any]  # Full PR object (large, nested)


class IssuesEventPayload(TypedDict):
    """Payload structure for IssuesEvent."""

    action: str  # Action: opened, closed, reopened, labeled, etc.
    issue: Dict[str, Any]  # Full issue object


class WatchEventPayload(TypedDict):
    """Payload structure for WatchEvent (repository star)."""

    action: str  # Always "started" (user starred the repo)


class ForkEventPayload(TypedDict):
    """Payload structure for ForkEvent."""

    forkee: Dict[str, Any]  # The forked repository object


# Event Type to Payload Mapping
EVENT_PAYLOAD_TYPES = {
    EventType.PUSH_EVENT: PushEventPayload,
    EventType.PULL_REQUEST_EVENT: PullRequestEventPayload,
    EventType.ISSUES_EVENT: IssuesEventPayload,
    EventType.WATCH_EVENT: WatchEventPayload,
    EventType.FORK_EVENT: ForkEventPayload,
    # Add more as needed
}


# Commonly Used Event Types for Recruitment
RECRUITMENT_EVENT_TYPES = [
    EventType.PUSH_EVENT,  # Commits (code contributions)
    EventType.PULL_REQUEST_EVENT,  # PRs (collaboration, code review)
    EventType.ISSUES_EVENT,  # Issues (problem-solving, communication)
    EventType.ISSUE_COMMENT_EVENT,  # Comments (engagement, helpfulness)
]


# Trending Detection Event Types
TRENDING_EVENT_TYPES = [
    EventType.WATCH_EVENT,  # Stars (popularity)
    EventType.FORK_EVENT,  # Forks (adoption)
]


# Programming Languages Tracked by GitHub
# Reference: https://github.com/github/linguist
COMMON_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Go",
    "Rust",
    "C",
    "C++",
    "C#",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "Scala",
    "Shell",
    "HTML",
    "CSS",
    "SQL",
    "R",
    "Objective-C",
    "Dart",
    "Elixir",
    "Haskell",
    "Lua",
    "Perl",
    "Clojure",
]


# Table Naming Conventions
def get_table_name(year: int, month: int, day: int) -> str:
    """
    Get GHArchive table name for specific date.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day (1-31)

    Returns:
        Table name (e.g., "githubarchive.day.20250113")
    """
    return f"githubarchive.day.{year:04d}{month:02d}{day:02d}"


def get_table_wildcard(year: Optional[int] = None, month: Optional[int] = None) -> str:
    """
    Get GHArchive table wildcard pattern.

    Args:
        year: Year (optional, e.g., 2025)
        month: Month (optional, 1-12)

    Returns:
        Wildcard pattern (e.g., "githubarchive.day.2025*" or "githubarchive.day.202501*")

    Examples:
        >>> get_table_wildcard(2025)
        'githubarchive.day.2025*'

        >>> get_table_wildcard(2025, 1)
        'githubarchive.day.202501*'

        >>> get_table_wildcard()
        'githubarchive.day.*'
    """
    if year is None:
        return "githubarchive.day.*"
    elif month is None:
        return f"githubarchive.day.{year:04d}*"
    else:
        return f"githubarchive.day.{year:04d}{month:02d}*"


def get_table_suffix_filter(start_date: str, end_date: str) -> str:
    """
    Generate _TABLE_SUFFIX BETWEEN clause for partition filtering.

    CRITICAL for cost optimization - reduces data scanned by 90%+.

    Args:
        start_date: Start date in YYYYMMDD format (e.g., "20250101")
        end_date: End date in YYYYMMDD format (e.g., "20250131")

    Returns:
        SQL clause (e.g., "_TABLE_SUFFIX BETWEEN '20250101' AND '20250131'")

    Example:
        >>> get_table_suffix_filter("20250101", "20250131")
        "_TABLE_SUFFIX BETWEEN '20250101' AND '20250131'"
    """
    return f"_TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'"


# Data Size Estimates (for cost calculation)
# These are approximate averages as of 2025
ESTIMATED_GB_PER_DAY = 2.5  # Average GB per day table
ESTIMATED_GB_PER_MONTH = 75.0  # Average GB per month (30 days)


def estimate_data_size_gb(days: int) -> float:
    """
    Estimate data size in GB for date range.

    Args:
        days: Number of days to query

    Returns:
        Estimated GB to scan

    Example:
        >>> estimate_data_size_gb(30)
        75.0
    """
    return days * ESTIMATED_GB_PER_DAY


def estimate_query_cost_usd(days: int, cost_per_tb: float = 6.25) -> float:
    """
    Estimate BigQuery query cost.

    Args:
        days: Number of days to query
        cost_per_tb: Cost per TB scanned (default: $6.25 as of 2025)

    Returns:
        Estimated cost in USD

    Example:
        >>> estimate_query_cost_usd(30)
        0.46875
    """
    gb_scanned = estimate_data_size_gb(days)
    tb_scanned = gb_scanned / 1024
    return tb_scanned * cost_per_tb


# Notes:
# - GHArchive only captures public events (no private repository data)
# - Events are added hourly (1-hour delay from real-time)
# - Historical data available from 2011 onwards
# - Table structure may change over time (GHArchive updates)
# - Some event types deprecated (e.g., FollowEvent no longer tracked)
