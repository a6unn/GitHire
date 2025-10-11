"""
Integration Test: Layer 1 - Profile Field Extraction
Module 010: Contact Enrichment

Tests the ProfileExtractor service's ability to extract contact info from GitHub profiles.
These tests MUST FAIL initially (TDD).
"""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_extract_profile_with_email():
    """
    Test: Extract profile fields when email is public
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    # Mock GitHub API response with email
    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": "test@gmail.com",
        "blog": "https://testuser.com",
        "twitter_username": "testuser",
        "company": "Test Corp",
        "hireable": True,
    }

    result = await extractor.extract(profile_data)

    assert result["primary_email"] == "test@gmail.com"
    assert result["blog_url"] == "https://testuser.com"
    assert result["twitter_username"] == "testuser"
    assert result["company"] == "Test Corp"
    assert result["hireable"] is True
    assert result["contact_sources"]["primary_email"] == "profile"


@pytest.mark.asyncio
async def test_extract_profile_without_email():
    """
    Test: Extract profile fields when email is private
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    # Profile with no email
    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": None,
        "blog": "https://testuser.com",
        "twitter_username": None,
        "company": None,
        "hireable": False,
    }

    result = await extractor.extract(profile_data)

    assert result["primary_email"] is None
    assert result["blog_url"] == "https://testuser.com"
    assert result["twitter_username"] is None
    assert result["company"] is None
    assert result["hireable"] is False


@pytest.mark.asyncio
async def test_extract_profile_filters_noreply_email():
    """
    Test: Noreply email from profile is filtered out
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    # Profile with noreply email
    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": "testuser@users.noreply.github.com",
        "blog": None,
        "twitter_username": None,
        "company": None,
        "hireable": False,
    }

    result = await extractor.extract(profile_data)

    # Noreply should be treated as None
    assert result["primary_email"] is None


@pytest.mark.asyncio
async def test_extract_profile_filters_spam_domain():
    """
    Test: Spam domain email from profile is filtered out
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    # Profile with spam domain
    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": "fake@example.com",
        "blog": None,
        "twitter_username": None,
        "company": None,
        "hireable": False,
    }

    result = await extractor.extract(profile_data)

    # Spam domain should be filtered
    assert result["primary_email"] is None


@pytest.mark.asyncio
async def test_extract_profile_normalizes_twitter_url():
    """
    Test: Twitter URL in profile is normalized to username
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    # Profile with Twitter URL instead of username
    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": None,
        "blog": None,
        "twitter_username": "https://twitter.com/testuser",  # URL instead of username
        "company": None,
        "hireable": False,
    }

    result = await extractor.extract(profile_data)

    # Should normalize to just username
    assert result["twitter_username"] == "testuser"


@pytest.mark.asyncio
async def test_extract_profile_handles_blog_without_protocol():
    """
    Test: Blog URL without protocol is handled
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": None,
        "blog": "testuser.com",  # No https://
        "twitter_username": None,
        "company": None,
        "hireable": False,
    }

    result = await extractor.extract(profile_data)

    # Should add protocol
    assert result["blog_url"] in ["https://testuser.com", "http://testuser.com"]


@pytest.mark.asyncio
async def test_extract_profile_records_contact_sources():
    """
    Test: Contact sources are properly recorded
    Expected: FAIL - ProfileExtractor not implemented
    """
    from src.contact_enrichment.services.profile_extractor import ProfileExtractor

    extractor = ProfileExtractor(github_token="fake_token")

    profile_data = {
        "login": "testuser",
        "name": "Test User",
        "email": "test@gmail.com",
        "blog": "https://testuser.com",
        "twitter_username": "testuser",
        "company": "Test Corp",
        "hireable": True,
    }

    result = await extractor.extract(profile_data)

    # All sources should be "profile"
    assert result["contact_sources"]["primary_email"] == "profile"
    assert result["contact_sources"]["blog_url"] == "profile"
    assert result["contact_sources"]["twitter_username"] == "profile"
