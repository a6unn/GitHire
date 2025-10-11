"""
ContactInfo Model
Module 010: Contact Enrichment

Represents enriched contact information for a GitHub candidate.
GDPR-compliant with retention and collection basis tracking.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    """
    Contact information extracted from a GitHub profile.

    Constitutional Rules Applied:
    - CR-001: Privacy-First - All fields optional except GDPR fields
    - CR-002: GDPR Compliance - Includes collection basis and retention
    - CR-004: Transparency - Records source for each contact method
    """

    # GitHub identity (required)
    github_username: str = Field(..., description="GitHub username (primary key)")

    # Contact fields (all optional - not all candidates have all contact methods)
    primary_email: Optional[str] = Field(
        None, description="Best quality email found (deduplicated, validated)"
    )
    additional_emails: list[str] = Field(
        default_factory=list, description="Other valid emails found"
    )
    linkedin_username: Optional[str] = Field(
        None, description="LinkedIn username (normalized from URL)"
    )
    twitter_username: Optional[str] = Field(
        None, description="Twitter/X username (normalized from URL/handle)"
    )
    blog_url: Optional[str] = Field(None, description="Personal website/blog URL")
    company: Optional[str] = Field(None, description="Current company from profile")
    hireable: bool = Field(False, description="Hireable flag from GitHub profile")

    # Transparency: Track where each contact method was found
    contact_sources: dict[str, str] = Field(
        ...,
        description="Source for each contact method (profile, commit, readme, blog, bio)",
    )

    # GDPR Compliance fields (required)
    enriched_at: datetime = Field(
        ..., description="When this contact information was collected (UTC)"
    )
    gdpr_collection_basis: str = Field(
        ...,
        description="Legal basis for collection (e.g., legitimate_interest_recruiting)",
    )
    data_retention_expires_at: datetime = Field(
        ..., description="When this data should be deleted (GDPR retention period)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "github_username": "testuser",
                "primary_email": "test@gmail.com",
                "additional_emails": ["alt@company.com"],
                "linkedin_username": "testuser",
                "twitter_username": "testuser",
                "blog_url": "https://testuser.dev",
                "company": "Acme Corp",
                "hireable": True,
                "contact_sources": {
                    "primary_email": "commit",
                    "linkedin_username": "readme",
                    "twitter_username": "profile",
                },
                "enriched_at": "2025-10-10T12:00:00Z",
                "gdpr_collection_basis": "legitimate_interest_recruiting",
                "data_retention_expires_at": "2025-11-09T12:00:00Z",
            }
        }
