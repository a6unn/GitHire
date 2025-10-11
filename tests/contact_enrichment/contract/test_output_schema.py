"""
Contract Test: Output Schema Validation
Module 010: Contact Enrichment

Tests that the output (ContactInfo, EnrichmentResult) matches expected schema.
These tests MUST FAIL initially (TDD).
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError


def test_valid_contact_info_passes_validation():
    """
    Test: Valid ContactInfo object passes schema validation
    Expected: FAIL - ContactInfo model doesn't exist
    """
    from src.contact_enrichment.models.contact_info import ContactInfo

    # Create valid ContactInfo
    contact = ContactInfo(
        github_username="testuser",
        primary_email="test@example.com",
        additional_emails=["alt@example.com"],
        linkedin_username="testuser",
        twitter_username="testuser",
        blog_url="https://testuser.com",
        company="Test Corp",
        hireable=True,
        contact_sources={
            "primary_email": "profile",
            "linkedin_username": "readme"
        },
        enriched_at=datetime.utcnow(),
        gdpr_collection_basis="legitimate_interest_recruiting",
        data_retention_expires_at=datetime.utcnow() + timedelta(days=30)
    )

    # Should create without error
    assert contact.primary_email == "test@example.com"
    assert contact.linkedin_username == "testuser"


def test_valid_enrichment_result_passes_validation():
    """
    Test: Valid EnrichmentResult metadata passes schema validation
    Expected: FAIL - EnrichmentResult model doesn't exist
    """
    from src.contact_enrichment.models.enrichment_result import EnrichmentResult

    result = EnrichmentResult(
        total_candidates=10,
        successfully_enriched=8,
        email_found_count=6,
        linkedin_found_count=3,
        twitter_found_count=7,
        website_found_count=9,
        average_contacts_per_candidate=2.5,
        enrichment_time_ms=5000,
        api_calls_made=30,
        rate_limit_remaining=4970,
        failed_enrichments=["user1", "user2"]
    )

    assert result.total_candidates == 10
    assert result.successfully_enriched == 8


def test_contact_info_with_null_email_is_valid():
    """
    Test: ContactInfo with primary_email=None is valid (not all candidates have emails)
    Expected: FAIL - ContactInfo model doesn't exist
    """
    from src.contact_enrichment.models.contact_info import ContactInfo

    contact = ContactInfo(
        github_username="testuser",
        primary_email=None,  # No email found
        additional_emails=[],
        linkedin_username="testuser",
        twitter_username=None,
        blog_url="https://testuser.com",
        company=None,
        hireable=False,
        contact_sources={"linkedin_username": "readme"},
        enriched_at=datetime.utcnow(),
        gdpr_collection_basis="legitimate_interest_recruiting",
        data_retention_expires_at=datetime.utcnow() + timedelta(days=30)
    )

    # Should be valid even without email
    assert contact.primary_email is None
    assert contact.linkedin_username == "testuser"


def test_contact_sources_field_is_required():
    """
    Test: contact_sources field is required in ContactInfo
    Expected: FAIL - ContactInfo model doesn't exist
    """
    from src.contact_enrichment.models.contact_info import ContactInfo

    # Missing contact_sources should fail
    with pytest.raises(ValidationError):
        contact = ContactInfo(
            primary_email="test@example.com",
            additional_emails=[],
            linkedin_username=None,
            twitter_username=None,
            blog_url=None,
            company=None,
            hireable=False,
            # contact_sources missing!
            enriched_at=datetime.utcnow(),
            gdpr_collection_basis="legitimate_interest_recruiting",
            data_retention_expires_at=datetime.utcnow() + timedelta(days=30)
        )


def test_enriched_at_and_expires_at_timestamps_are_valid():
    """
    Test: enriched_at and data_retention_expires_at are valid timestamps
    Expected: FAIL - ContactInfo model doesn't exist
    """
    from src.contact_enrichment.models.contact_info import ContactInfo

    now = datetime.utcnow()
    expires = now + timedelta(days=30)

    contact = ContactInfo(
        github_username="testuser",
        primary_email="test@example.com",
        additional_emails=[],
        linkedin_username=None,
        twitter_username=None,
        blog_url=None,
        company=None,
        hireable=False,
        contact_sources={"primary_email": "profile"},
        enriched_at=now,
        gdpr_collection_basis="legitimate_interest_recruiting",
        data_retention_expires_at=expires
    )

    assert contact.enriched_at == now
    assert contact.data_retention_expires_at == expires
    assert contact.data_retention_expires_at > contact.enriched_at
