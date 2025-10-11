"""SearchResult model for search execution metadata.

Provides transparency about GitHub search results and API usage.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime


class SearchResult(BaseModel):
    """Metadata about search execution."""

    total_candidates_found: int = Field(..., ge=0, description="Total matches on GitHub")
    candidates_returned: int = Field(
        ..., ge=0, le=25, description="Number returned (max 25)"
    )
    search_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When search was executed"
    )
    rate_limit_remaining: int = Field(..., ge=0, description="GitHub API quota remaining")
    cache_hit: bool = Field(..., description="Whether results came from cache")
    execution_time_ms: int = Field(..., ge=0, description="Search duration in milliseconds")

    # Optional warnings
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings (e.g., rate limit low, partial results)",
    )

    @field_validator("candidates_returned")
    @classmethod
    def validate_max_25(cls, v: int, info) -> int:
        """Ensure candidates_returned does not exceed 25."""
        if v > 25:
            raise ValueError("Cannot return more than 25 candidates")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_candidates_found": 1247,
                "candidates_returned": 25,
                "search_timestamp": "2025-10-06T10:30:00Z",
                "rate_limit_remaining": 4875,
                "cache_hit": False,
                "execution_time_ms": 3420,
                "warnings": [],
            }
        }
    )
