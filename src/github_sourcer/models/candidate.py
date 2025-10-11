"""Candidate model for GitHub developer profiles.

Represents a GitHub user with repositories and activity data.
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator, model_validator, ConfigDict
from typing import Optional, Any
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
    github_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL")  # New field
    email: Optional[EmailStr] = Field(None, description="Email if available")  # Alias for public_email

    # Profile info
    bio: Optional[str] = Field(None, description="User bio/description")
    location: Optional[str] = Field(None, description="Geographic location")

    # Skills (legacy field - kept for backward compatibility)
    skills: list[str] = Field(
        default_factory=list, description="Detected technical skills"
    )

    # GitHub data
    top_repos: list[Repository] = Field(
        default_factory=list, description="Top 5 repositories by stars"
    )
    languages: list[str] = Field(
        default_factory=list, description="Programming languages from repos"
    )
    contribution_count: int = Field(default=0, ge=0, description="Total contributions in last year")
    account_age_days: int = Field(default=0, ge=0, description="Days since account creation")
    followers: int = Field(default=0, ge=0, description="Follower count")
    public_repos: int = Field(default=0, ge=0, description="Number of public repositories")

    # URLs
    profile_url: Optional[HttpUrl] = Field(None, description="GitHub profile URL (deprecated, use github_url)")
    avatar_url: Optional[HttpUrl] = Field(None, description="Profile image URL")

    # Metadata
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when data was fetched"
    )

    # ========================================================================
    # Enhanced Fields for Module 002: GitHub Sourcer Integration (FR-003 to FR-009)
    # ========================================================================

    # FR-003: Skill confidence scores
    skill_confidence_scores: Optional[dict[str, float]] = Field(
        default=None,
        description="Confidence scores (0.0-1.0) for each detected skill"
    )

    # FR-004: Parsed location hierarchy
    location_parsed: Optional[dict[str, Any]] = Field(
        default=None,
        description="Hierarchical location breakdown (city, state, country, confidence, matched_via)"
    )

    # FR-005: Sourcing metadata
    sourcing_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Pipeline metadata (discovered_via, skills_detected_via, processing_timestamp, etc.)"
    )

    # FR-006: Detection method
    detection_method: Optional[str] = Field(
        default=None,
        description="Skills detection method used (dependency_graph, ensemble_fallback, manual)"
    )

    # Matching metadata
    match_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall match score (0.0-1.0)")
    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills that matched the job requirements"
    )

    @field_validator("top_repos")
    @classmethod
    def truncate_repos_to_5(cls, v: list[Repository]) -> list[Repository]:
        """Ensure top_repos contains maximum 5 repositories."""
        if len(v) > 5:
            return v[:5]
        return v

    @field_validator("languages")
    @classmethod
    def deduplicate_and_sort_languages(cls, v: list[str]) -> list[str]:
        """Deduplicate and sort languages alphabetically."""
        if not v:
            return []
        # Remove duplicates and sort
        return sorted(set(v))

    @field_validator("skill_confidence_scores")
    @classmethod
    def validate_skill_confidence_range(cls, v: Optional[dict[str, float]]) -> Optional[dict[str, float]]:
        """Validate that all confidence scores are in range 0.0-1.0 (BR-004)."""
        if v is None:
            return v
        for skill, score in v.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Confidence score for '{skill}' must be between 0.0 and 1.0, got {score}")
        return v

    @field_validator("github_url")
    @classmethod
    def validate_github_url_format(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Validate that github_url is a valid GitHub profile URL (BR-007)."""
        if v is None:
            return v
        url_str = str(v)
        if not url_str.startswith("https://github.com/"):
            raise ValueError(f"github_url must be a valid GitHub profile URL, got {url_str}")
        # Extract username part
        username_part = url_str.replace("https://github.com/", "")
        if "/" in username_part or not username_part:
            raise ValueError(f"github_url must point to a user profile, not a repository or organization, got {url_str}")
        return v

    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate business rules for Candidate model."""
        # BR-001: skill_confidence_scores keys must be subset of skills
        if self.skill_confidence_scores and self.skills:
            confidence_skills = set(self.skill_confidence_scores.keys())
            available_skills = set(self.skills)
            extra_skills = confidence_skills - available_skills
            if extra_skills:
                raise ValueError(
                    f"skill_confidence_scores contains skills not in skills list: {extra_skills}"
                )

        # BR-002: match_score must not exceed max(skill_confidence_scores)
        if self.skill_confidence_scores and len(self.skill_confidence_scores) > 0:
            max_confidence = max(self.skill_confidence_scores.values())
            if self.match_score > max_confidence:
                raise ValueError(
                    f"match_score ({self.match_score}) cannot exceed maximum skill confidence ({max_confidence})"
                )

        # BR-005: matched_skills must be subset of skills
        if self.matched_skills and self.skills:
            matched_set = set(self.matched_skills)
            skills_set = set(self.skills)
            extra_matched = matched_set - skills_set
            if extra_matched:
                raise ValueError(
                    f"matched_skills contains skills not in skills list: {extra_matched}"
                )

        # BR-006: detection_method must be from allowed values
        if self.detection_method is not None:
            allowed_methods = {"dependency_graph", "ensemble_fallback", "manual"}
            if self.detection_method not in allowed_methods:
                raise ValueError(
                    f"detection_method must be one of {allowed_methods}, got '{self.detection_method}'"
                )

        # BR-003: Validate location_parsed confidence matches method
        if self.location_parsed:
            confidence = self.location_parsed.get("confidence", 0.0)
            matched_via = self.location_parsed.get("matched_via", "")

            if matched_via == "city_exact" and confidence < 0.95:
                raise ValueError(
                    f"city_exact match should have confidence >= 0.95, got {confidence}"
                )
            elif matched_via == "city_fuzzy" and confidence >= 1.0:
                raise ValueError(
                    f"city_fuzzy match should have confidence < 1.0, got {confidence}"
                )
            elif matched_via == "state_exact" and not (0.60 <= confidence <= 0.80):
                raise ValueError(
                    f"state_exact match should have confidence between 0.60 and 0.80, got {confidence}"
                )
            elif matched_via == "country_exact" and not (0.30 <= confidence <= 0.50):
                raise ValueError(
                    f"country_exact match should have confidence between 0.30 and 0.50, got {confidence}"
                )

        return self

    model_config = ConfigDict(
        json_schema_extra={
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
                        "url": "https://github.com/torvalds/linux",
                    }
                ],
                "languages": ["C", "Assembly", "Shell"],
                "contribution_count": 2500,
                "account_age_days": 5000,
                "followers": 200000,
                "profile_url": "https://github.com/torvalds",
                "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
                "fetched_at": "2025-10-06T10:30:00Z",
            }
        }
    )
