"""
EnrichmentResult Model
Module 010: Contact Enrichment

Represents metadata and statistics from a batch enrichment operation.
"""

from pydantic import BaseModel, Field


class EnrichmentResult(BaseModel):
    """
    Metadata and statistics from a contact enrichment batch operation.

    Used for monitoring, analytics, and validating enrichment quality.
    """

    # Overall statistics
    total_candidates: int = Field(..., description="Total candidates processed")
    successfully_enriched: int = Field(
        ..., description="Candidates successfully enriched (at least one contact found)"
    )

    # Contact method success rates
    email_found_count: int = Field(..., description="Candidates with email found")
    linkedin_found_count: int = Field(
        ..., description="Candidates with LinkedIn found"
    )
    twitter_found_count: int = Field(..., description="Candidates with Twitter found")
    website_found_count: int = Field(
        ..., description="Candidates with blog/website found"
    )

    # Enrichment quality metrics
    average_contacts_per_candidate: float = Field(
        ..., description="Average number of contact methods found per candidate"
    )

    # Performance metrics
    enrichment_time_ms: int = Field(
        ..., description="Total time taken for enrichment (milliseconds)"
    )

    # API usage tracking
    api_calls_made: int = Field(..., description="Total GitHub API calls made")
    rate_limit_remaining: int = Field(
        ..., description="GitHub API rate limit remaining after enrichment"
    )

    # Error tracking
    failed_enrichments: list[str] = Field(
        default_factory=list,
        description="GitHub usernames that failed enrichment (for debugging)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_candidates": 10,
                "successfully_enriched": 9,
                "email_found_count": 7,
                "linkedin_found_count": 3,
                "twitter_found_count": 6,
                "website_found_count": 8,
                "average_contacts_per_candidate": 2.4,
                "enrichment_time_ms": 5000,
                "api_calls_made": 30,
                "rate_limit_remaining": 4970,
                "failed_enrichments": ["user_with_no_data"],
            }
        }
