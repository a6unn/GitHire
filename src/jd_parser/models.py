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

    @model_validator(mode='after')
    def validate_minimum_fields(self):
        """Ensure at least role OR required_skills is present (FR-011)."""
        if not self.role and len(self.required_skills) == 0:
            raise ValueError(
                "At least one of 'role' or 'required_skills' must be present. "
                "Job description is too vague to extract meaningful requirements."
            )
        return self
