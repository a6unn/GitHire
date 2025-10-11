"""
Integration Test: Full Contact Enrichment Pipeline
Module 010: Contact Enrichment

Tests the ContactEnricher orchestrator's ability to run the full enrichment pipeline.
These tests MUST FAIL initially (TDD).
"""

import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_enrich_single_candidate():
    """
    Test: Enrich single candidate with all 4 layers
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidate = {
        "github_username": "testuser",
        "name": "Test User",
        "bio": "Software Engineer | @testuser",
        "location": "San Francisco, CA",
        "top_repos": [],
        "languages": ["Python"],
        "contribution_count": 100,
        "account_age_days": 365,
        "profile_url": "https://github.com/testuser",
        "avatar_url": "https://avatars.githubusercontent.com/u/123",
        "fetched_at": "2025-10-10T00:00:00Z",
    }

    result = await enricher.enrich(candidate)

    # Should return ContactInfo model
    assert result.github_username == "testuser"
    assert result.enriched_at is not None
    assert result.data_retention_expires_at is not None
    assert result.gdpr_collection_basis == "legitimate_interest_recruiting"


@pytest.mark.asyncio
async def test_enrich_multiple_candidates():
    """
    Test: Enrich multiple candidates concurrently
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidates = [
        {"github_username": "user1", "name": "User 1", "bio": "Developer"},
        {"github_username": "user2", "name": "User 2", "bio": "Engineer"},
        {"github_username": "user3", "name": "User 3", "bio": "Architect"},
    ]

    results = await enricher.enrich_batch(candidates)

    assert len(results) == 3
    assert all(r.github_username in ["user1", "user2", "user3"] for r in results)


@pytest.mark.asyncio
async def test_enrichment_pipeline_layers():
    """
    Test: All 4 layers are executed in pipeline
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidate = {
        "github_username": "testuser",
        "name": "Test User",
        "bio": "Engineer | @testuser | linkedin.com/in/testuser",
        "location": "NYC",
        "top_repos": [],
        "languages": ["Python"],
        "contribution_count": 50,
        "account_age_days": 200,
        "profile_url": "https://github.com/testuser",
        "avatar_url": "https://avatars.githubusercontent.com/u/1",
        "fetched_at": "2025-10-10T00:00:00Z",
    }

    result = await enricher.enrich(candidate)

    # Verify contact_sources contains data from multiple layers
    assert "contact_sources" in result.__dict__
    sources = result.contact_sources

    # Should have sources from different layers
    assert isinstance(sources, dict)


@pytest.mark.asyncio
async def test_enrichment_returns_metadata():
    """
    Test: Enrichment returns EnrichmentResult metadata
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidates = [
        {"github_username": "user1", "name": "User 1", "bio": "Developer"},
        {"github_username": "user2", "name": "User 2", "bio": "Engineer"},
    ]

    contact_results, metadata = await enricher.enrich_batch_with_metadata(candidates)

    # Verify metadata structure
    assert metadata.total_candidates == 2
    assert metadata.successfully_enriched >= 0
    assert metadata.enrichment_time_ms > 0
    assert isinstance(metadata.failed_enrichments, list)


@pytest.mark.asyncio
async def test_enrichment_handles_invalid_candidate():
    """
    Test: Invalid candidate is handled gracefully
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    # Missing github_username
    candidate = {"name": "Test User", "bio": "Developer"}

    with pytest.raises(ValueError):
        await enricher.enrich(candidate)


@pytest.mark.asyncio
async def test_enrichment_respects_rate_limits():
    """
    Test: Enrichment respects GitHub API rate limits
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token", max_concurrent=5)

    candidates = [{"github_username": f"user{i}", "name": f"User {i}"} for i in range(20)]

    _, metadata = await enricher.enrich_batch_with_metadata(candidates)

    # Should track API calls
    assert metadata.api_calls_made > 0
    assert hasattr(metadata, "rate_limit_remaining")


@pytest.mark.asyncio
async def test_enrichment_sets_gdpr_fields():
    """
    Test: GDPR fields are properly set
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(
        github_token="fake_token", retention_days=30  # Custom retention
    )

    candidate = {"github_username": "testuser", "name": "Test User", "bio": "Developer"}

    result = await enricher.enrich(candidate)

    # Verify GDPR fields
    assert result.enriched_at is not None
    assert result.data_retention_expires_at is not None
    assert result.gdpr_collection_basis == "legitimate_interest_recruiting"

    # Verify retention period
    expected_expiry = result.enriched_at + timedelta(days=30)
    assert abs((result.data_retention_expires_at - expected_expiry).total_seconds()) < 1


@pytest.mark.asyncio
async def test_enrichment_deduplicates_emails():
    """
    Test: Emails from multiple layers are deduplicated
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidate = {
        "github_username": "testuser",
        "name": "Test User",
        "bio": "test@gmail.com",  # Email in bio
        "location": "NYC",
        "top_repos": [],
        "languages": ["Python"],
        "contribution_count": 50,
        "account_age_days": 200,
        "profile_url": "https://github.com/testuser",
        "avatar_url": "https://avatars.githubusercontent.com/u/1",
        "fetched_at": "2025-10-10T00:00:00Z",
    }

    result = await enricher.enrich(candidate)

    # If same email found in multiple layers, should be deduplicated
    if result.additional_emails:
        # Should not have duplicates
        assert len(result.additional_emails) == len(set(result.additional_emails))


@pytest.mark.asyncio
async def test_enrichment_logs_failed_candidates():
    """
    Test: Failed enrichments are logged in metadata
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidates = [
        {"github_username": "validuser", "name": "Valid User"},
        {"name": "Invalid User"},  # Missing github_username
    ]

    contact_results, metadata = await enricher.enrich_batch_with_metadata(
        candidates, skip_invalid=True
    )

    # Should log the failed enrichment
    assert len(metadata.failed_enrichments) > 0


@pytest.mark.asyncio
async def test_enrichment_prioritizes_best_email():
    """
    Test: Primary email is selected from best source
    Expected: FAIL - ContactEnricher not implemented
    """
    from src.contact_enrichment import ContactEnricher

    enricher = ContactEnricher(github_token="fake_token")

    candidate = {"github_username": "testuser", "name": "Test User", "bio": "Developer"}

    result = await enricher.enrich(candidate)

    # If multiple emails found, primary_email should be the best quality one
    if result.primary_email:
        assert "@" in result.primary_email
        # Should not be noreply or spam
        assert "noreply" not in result.primary_email.lower()
        assert "example.com" not in result.primary_email.lower()
