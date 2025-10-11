"""
Integration Test: Layer 4 - Social Profile Discovery
Module 010: Contact Enrichment

Tests the SocialDiscoverer service's ability to discover social profiles from bio/blog.
These tests MUST FAIL initially (TDD).
"""

import pytest


@pytest.mark.asyncio
async def test_discover_linkedin_from_bio():
    """
    Test: Discover LinkedIn username from bio text
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Software Engineer | linkedin.com/in/testuser | Python enthusiast"

    result = await discoverer.discover_from_bio(bio)

    assert result["linkedin_username"] == "testuser"
    assert result["contact_sources"]["linkedin_username"] == "bio"


@pytest.mark.asyncio
async def test_discover_twitter_from_bio():
    """
    Test: Discover Twitter username from bio text
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Developer @TestCompany | Follow me @testuser for tech content"

    result = await discoverer.discover_from_bio(bio)

    assert result["twitter_username"] == "testuser"
    assert result["contact_sources"]["twitter_username"] == "bio"


@pytest.mark.asyncio
async def test_discover_multiple_socials_from_bio():
    """
    Test: Discover multiple social profiles from bio
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Engineer | @testuser | linkedin.com/in/testuser | Rust & Python"

    result = await discoverer.discover_from_bio(bio)

    assert result["twitter_username"] == "testuser"
    assert result["linkedin_username"] == "testuser"


@pytest.mark.asyncio
async def test_discover_socials_from_blog_page():
    """
    Test: Discover social profiles by scraping blog page
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    # Mock blog HTML content
    blog_html = """
    <html>
    <body>
        <a href="https://twitter.com/testuser">Follow me on Twitter</a>
        <a href="https://linkedin.com/in/testuser">Connect on LinkedIn</a>
    </body>
    </html>
    """

    result = await discoverer.discover_from_blog(blog_html)

    assert result["twitter_username"] == "testuser"
    assert result["linkedin_username"] == "testuser"
    assert result["contact_sources"]["twitter_username"] == "blog"


@pytest.mark.asyncio
async def test_discover_handles_empty_bio():
    """
    Test: Empty bio returns empty result
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    result = await discoverer.discover_from_bio("")

    assert result["twitter_username"] is None
    assert result["linkedin_username"] is None


@pytest.mark.asyncio
async def test_discover_normalizes_twitter_url():
    """
    Test: Twitter URL in bio is normalized to username
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Developer | https://twitter.com/testuser | Python"

    result = await discoverer.discover_from_bio(bio)

    assert result["twitter_username"] == "testuser"


@pytest.mark.asyncio
async def test_discover_normalizes_linkedin_url():
    """
    Test: LinkedIn URL in bio is normalized to username
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Engineer | Connect: https://www.linkedin.com/in/testuser/ | Open source"

    result = await discoverer.discover_from_bio(bio)

    assert result["linkedin_username"] == "testuser"


@pytest.mark.asyncio
async def test_discover_handles_x_dot_com():
    """
    Test: x.com links are recognized as Twitter
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "Follow me on https://x.com/testuser"

    result = await discoverer.discover_from_bio(bio)

    assert result["twitter_username"] == "testuser"


@pytest.mark.asyncio
async def test_discover_from_blog_handles_404():
    """
    Test: 404 blog page returns empty result gracefully
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    # Simulate 404 response
    result = await discoverer.discover_from_blog(None)

    assert result["twitter_username"] is None
    assert result["linkedin_username"] is None


@pytest.mark.asyncio
async def test_discover_prioritizes_first_match():
    """
    Test: When multiple Twitter handles found, prioritize first
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    bio = "RT @someoneelse but follow @testuser for my content"

    result = await discoverer.discover_from_bio(bio)

    # Should prioritize the pattern that looks most like self-promotion
    # In this case, "follow @testuser" is more likely than RT
    assert result["twitter_username"] in ["testuser", "someoneelse"]


@pytest.mark.asyncio
async def test_discover_extracts_email_from_blog():
    """
    Test: Extract email from blog page
    Expected: FAIL - SocialDiscoverer not implemented
    """
    from src.contact_enrichment.services.social_discoverer import SocialDiscoverer

    discoverer = SocialDiscoverer(github_token="fake_token")

    blog_html = """
    <html>
    <body>
        <p>Contact me at: test@gmail.com</p>
    </body>
    </html>
    """

    result = await discoverer.discover_from_blog(blog_html)

    assert "test@gmail.com" in result["emails"]
    assert result["contact_sources"]["emails"] == "blog"
