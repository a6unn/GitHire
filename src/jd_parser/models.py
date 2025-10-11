"""Pydantic models for JD Parser module."""

from typing import Optional
from pydantic import BaseModel, Field, model_validator


class FreeTextInput(BaseModel):
    """Input schema for free-text job description."""

    text: str = Field(..., min_length=1, description="Free-text job description in English")
    language: str = Field(default="en", pattern="^en$", description="Input language (English only)")


class TextSpan(BaseModel):
    """Represents a highlighted span in the original text."""

    start: int = Field(..., ge=0, description="Start index in original text")
    end: int = Field(..., ge=0, description="End index in original text")
    text: str = Field(..., min_length=1, description="Highlighted text content")

    @model_validator(mode='after')
    def validate_span(self):
        """Ensure end > start."""
        if self.end <= self.start:
            raise ValueError(f"end ({self.end}) must be greater than start ({self.start})")
        return self


class ConfidenceScore(BaseModel):
    """Confidence score for an extracted field."""

    score: int = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    reasoning: str = Field(..., min_length=1, description="Why this confidence level")
    highlighted_spans: list[TextSpan] = Field(
        default_factory=list,
        description="Text spans that support this extraction"
    )


class YearsOfExperience(BaseModel):
    """Represents experience range or minimum years."""

    min: Optional[int] = Field(None, ge=0, description="Minimum years")
    max: Optional[int] = Field(None, ge=0, description="Maximum years")
    range_text: Optional[str] = Field(None, description="Original text (e.g., '5+ years')")

    @model_validator(mode='after')
    def validate_range(self):
        """Ensure min <= max if both provided."""
        if self.min is not None and self.max is not None:
            if self.min > self.max:
                raise ValueError(f"min ({self.min}) cannot be greater than max ({self.max})")
        return self


class JobRequirement(BaseModel):
    """Structured job requirements extracted from free-text JD."""

    role: Optional[str] = Field(None, min_length=1, description="Extracted job role/title")
    required_skills: list[str] = Field(
        default_factory=list,
        description="Must-have technical skills (normalized)"
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        description="Nice-to-have skills (normalized)"
    )
    years_of_experience: YearsOfExperience = Field(
        default_factory=lambda: YearsOfExperience(min=None, max=None, range_text=None),
        description="Experience requirements"
    )
    seniority_level: Optional[str] = Field(
        None,
        pattern="^(Junior|Mid-level|Senior|Staff|Principal)$",
        description="Seniority level if specified"
    )
    location_preferences: list[str] = Field(
        default_factory=list,
        description="Preferred locations or 'Remote'"
    )
    domain: Optional[str] = Field(None, description="Industry/domain context (e.g., 'Fintech')")
    confidence_scores: dict[str, ConfidenceScore] = Field(
        default_factory=dict,
        description="Confidence scores for each extracted field"
    )
    original_input: str = Field(..., min_length=1, description="Original job description text")
    schema_version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Schema version (semver)"
    )

    # ========================================================================
    # Enhanced Fields for Module 002: GitHub Sourcer Integration (FR-025 to FR-032)
    # ========================================================================

    # FR-025: Sourcing source configuration
    sourcing_source_config: Optional[dict[str, bool]] = Field(
        default=None,
        description="Which sourcing channels to use (github_enabled, linkedin_enabled, etc.)"
    )

    # FR-026: Skills detection configuration
    skill_confidence_min: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold (0.0-1.0) for skill detection"
    )

    # FR-027, FR-028: Location filtering configuration
    location_hierarchy_enabled: bool = Field(
        default=True,
        description="Enable hierarchical location matching (city→state→country)"
    )
    location_fuzzy_match_enabled: bool = Field(
        default=True,
        description="Enable fuzzy matching for location names (e.g., Bangalore → Bengaluru)"
    )
    location_fuzzy_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0.0-1.0) for fuzzy location matching"
    )

    # FR-029: BigQuery discovery configuration
    bigquery_discovery_enabled: bool = Field(
        default=False,
        description="Use BigQuery/GHArchive for candidate discovery (optional, Step 1)"
    )
    bigquery_time_range_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Time range in days for BigQuery GHArchive queries"
    )

    # FR-030: GraphQL batching configuration
    graphql_batching_enabled: bool = Field(
        default=True,
        description="Enable GraphQL batching for profile enrichment (4.6x speedup)"
    )
    graphql_batch_size: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of profiles to fetch per GraphQL batch request"
    )

    # FR-031: Dependency Graph detection configuration
    dependency_graph_enabled: bool = Field(
        default=True,
        description="Use GitHub Dependency Graph API for skills detection (primary method)"
    )
    dependency_graph_fallback_to_ensemble: bool = Field(
        default=True,
        description="Fall back to ensemble scoring if Dependency Graph fails"
    )

    # FR-032: Output configuration
    max_candidates: int = Field(
        default=25,
        ge=1,
        le=5000,
        description="Maximum number of candidates to return"
    )

    @model_validator(mode='after')
    def validate_minimum_fields(self):
        """Ensure at least role OR required_skills is present (FR-011)."""
        if not self.role and len(self.required_skills) == 0:
            raise ValueError(
                "At least one of 'role' or 'required_skills' must be present. "
                "Job description is too vague to extract meaningful requirements."
            )
        return self
