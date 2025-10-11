# Data Model: GitHub Sourcer Module

**Date**: 2025-10-06
**Module**: 002-github-sourcer-module

---

## Overview

This module defines 3 entities:
1. **Candidate** - Output entity (GitHub developer profile)
2. **SearchCriteria** - Internal entity (processed search parameters)
3. **SearchResult** - Output metadata (search execution details)

---

## Entity 1: Candidate (Output)

**Purpose**: Represents a GitHub developer profile with repositories and activity data.

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class Repository(BaseModel):
    """A GitHub repository belonging to a candidate."""
    name: str = Field(..., min_length=1, description="Repository name")
    description: Optional[str] = Field(None, description="Repo description")
    stars: int = Field(..., ge=0, description="Star count")
    forks: int = Field(..., ge=0, description="Fork count")
    languages: list[str] = Field(default_factory=list, description="Programming languages used")
    url: HttpUrl = Field(..., description="GitHub repo URL")


class Candidate(BaseModel):
    """A GitHub developer candidate profile."""

    # Core identifiers
    github_username: str = Field(..., min_length=1, description="GitHub username (unique)")
    name: Optional[str] = Field(None, description="Display name")

    # Profile info
    bio: Optional[str] = Field(None, description="User bio/description")
    location: Optional[str] = Field(None, description="Geographic location")
    public_email: Optional[str] = Field(None, description="Public email if available")

    # GitHub data
    top_repos: list[Repository] = Field(
        default_factory=list,
        description="Top 5 repositories by stars"
    )
    languages: list[str] = Field(
        default_factory=list,
        description="Programming languages from repos"
    )
    contribution_count: int = Field(..., ge=0, description="Total contributions in last year")
    account_age_days: int = Field(..., ge=0, description="Days since account creation")
    followers: int = Field(default=0, ge=0, description="Follower count")

    # URLs
    profile_url: HttpUrl = Field(..., description="GitHub profile URL")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile image URL")

    # Metadata
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when data was fetched"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "github_username": "torvalds",
                "name": "Linus Torvalds",
                "bio": "Creator of Linux and Git",
                "location": "Portland, OR",
                "public_email": None,
                "top_repos": [
                    {
                        "name": "linux",
                        "description": "Linux kernel source tree",
                        "stars": 150000,
                        "forks": 50000,
                        "languages": ["C", "Assembly"],
                        "url": "https://github.com/torvalds/linux"
                    }
                ],
                "languages": ["C", "Assembly", "Shell"],
                "contribution_count": 2500,
                "account_age_days": 5000,
                "followers": 200000,
                "profile_url": "https://github.com/torvalds",
                "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
                "fetched_at": "2025-10-06T10:30:00Z"
            }
        }
```

**Validation Rules**:
- `github_username` is required and unique
- `contribution_count` >= 0
- `account_age_days` >= 0
- `top_repos` limited to 5 repositories
- `languages` deduplicated and sorted

---

## Entity 2: SearchCriteria (Internal)

**Purpose**: Processed search parameters derived from JobRequirement.

**Pydantic Model**:
```python
class SearchCriteria(BaseModel):
    """Internal representation of search parameters."""

    required_languages: list[str] = Field(
        default_factory=list,
        description="Programming languages from required_skills"
    )
    preferred_languages: list[str] = Field(
        default_factory=list,
        description="Programming languages from preferred_skills"
    )
    location_filter: Optional[str] = Field(
        None,
        description="Location filter (broadened to country if specific)"
    )
    min_account_age_days: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum account age (estimated from years_of_experience)"
    )
    activity_level: Optional[str] = Field(
        None,
        pattern="^(low|medium|high)$",
        description="Expected activity level (from seniority_level)"
    )

    # GitHub API query string
    query_string: str = Field(..., min_length=1, description="Constructed GitHub search query")

    @classmethod
    def from_job_requirement(cls, job_req: "JobRequirement") -> "SearchCriteria":
        """
        Construct SearchCriteria from JobRequirement.

        Args:
            job_req: JobRequirement from Module 001

        Returns:
            SearchCriteria with GitHub query constructed
        """
        # Map skills to GitHub languages
        required_langs = [
            SKILL_TO_GITHUB_LANGUAGE.get(skill.lower(), skill.lower())
            for skill in job_req.required_skills
        ]

        preferred_langs = [
            SKILL_TO_GITHUB_LANGUAGE.get(skill.lower(), skill.lower())
            for skill in job_req.preferred_skills
        ]

        # Broaden location to country (GitHub API limitation)
        location = None
        if job_req.location_preferences:
            # Simple heuristic: extract country or use first location
            location = cls._extract_country(job_req.location_preferences)

        # Estimate min account age from experience
        min_age_days = None
        if job_req.years_of_experience.min:
            min_age_days = job_req.years_of_experience.min * 365

        # Map seniority to activity level
        activity_level = cls._map_seniority_to_activity(job_req.seniority_level)

        # Build GitHub query string
        query = cls._build_query(
            required_langs=required_langs,
            preferred_langs=preferred_langs,
            location=location
        )

        return cls(
            required_languages=required_langs,
            preferred_languages=preferred_langs,
            location_filter=location,
            min_account_age_days=min_age_days,
            activity_level=activity_level,
            query_string=query
        )

    @staticmethod
    def _build_query(required_langs, preferred_langs, location) -> str:
        """Build GitHub search query string."""
        # Use primary language from required skills
        query_parts = []
        if required_langs:
            query_parts.append(f"language:{required_langs[0]}")
        elif preferred_langs:
            query_parts.append(f"language:{preferred_langs[0]}")

        if location:
            query_parts.append(f"location:{location}")

        # Add sort by followers (relevance)
        query_parts.append("sort:followers")

        return " ".join(query_parts)

    @staticmethod
    def _extract_country(locations: list[str]) -> str:
        """Extract country from location list."""
        # Simple heuristic: look for country names or use "india" as default
        for loc in locations:
            if any(country in loc.lower() for country in ["india", "usa", "uk", "canada"]):
                return loc.lower()
        return locations[0] if locations else "remote"

    @staticmethod
    def _map_seniority_to_activity(seniority: Optional[str]) -> Optional[str]:
        """Map seniority level to expected activity."""
        if not seniority:
            return None
        mapping = {
            "Junior": "low",
            "Mid-level": "medium",
            "Senior": "high",
            "Staff": "high",
            "Principal": "high"
        }
        return mapping.get(seniority)
```

---

## Entity 3: SearchResult (Output Metadata)

**Purpose**: Metadata about search execution (transparency requirement).

**Pydantic Model**:
```python
class SearchResult(BaseModel):
    """Metadata about search execution."""

    total_candidates_found: int = Field(..., ge=0, description="Total matches on GitHub")
    candidates_returned: int = Field(..., ge=0, le=25, description="Number returned (max 25)")
    search_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When search was executed"
    )
    rate_limit_remaining: int = Field(..., ge=0, description="GitHub API quota remaining")
    cache_hit: bool = Field(..., description="Whether results came from cache")
    execution_time_ms: int = Field(..., ge=0, description="Search duration in milliseconds")

    # Optional warnings
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings (e.g., rate limit low, partial results)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_candidates_found": 1247,
                "candidates_returned": 25,
                "search_timestamp": "2025-10-06T10:30:00Z",
                "rate_limit_remaining": 4875,
                "cache_hit": False,
                "execution_time_ms": 3420,
                "warnings": []
            }
        }
```

---

## Module Input/Output

### Input (from Module 001)
```python
from src.jd_parser.models import JobRequirement

# JD Parser output becomes GitHub Sourcer input
job_req: JobRequirement
```

### Output
```python
{
    "candidates": list[Candidate],  # Up to 25 candidates
    "metadata": SearchResult        # Search execution metadata
}
```

---

## Example Flow

```python
# Input from Module 001
job_req = JobRequirement(
    role="Senior Python Developer",
    required_skills=["Python", "FastAPI"],
    location_preferences=["Tamil Nadu"],
    years_of_experience=YearsOfExperience(min=5)
)

# Internal: Convert to SearchCriteria
criteria = SearchCriteria.from_job_requirement(job_req)
# criteria.query_string = "language:python location:india sort:followers"

# Execute search
candidates = search_github(criteria)  # Returns list[Candidate]

# Output with metadata
output = {
    "candidates": candidates[:25],  # Max 25
    "metadata": SearchResult(
        total_candidates_found=len(candidates),
        candidates_returned=min(len(candidates), 25),
        ...
    )
}
```

---

## Validation Summary

| Field | Validation | Error |
|-------|-----------|-------|
| github_username | Required, min_length=1 | "Username cannot be empty" |
| contribution_count | >= 0 | "Contributions must be non-negative" |
| account_age_days | >= 0 | "Account age must be non-negative" |
| candidates_returned | <= 25 | "Cannot return more than 25 candidates" |
| query_string | min_length=1 | "Query string cannot be empty" |

---

## Next: Create JSON Schemas

These models will be exported to JSON schemas in `/contracts/` for contract testing.
