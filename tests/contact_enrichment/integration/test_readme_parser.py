"""
Integration Test: Layer 3 - README Parsing
Module 010: Contact Enrichment

Tests the ReadmeParser service's ability to extract contact info from profile READMEs.
These tests MUST FAIL initially (TDD).
"""

import pytest


@pytest.mark.asyncio
async def test_parse_readme_with_linkedin_link():
    """
    Test: Extract LinkedIn username from README
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Hello, I'm Test User

    Connect with me on [LinkedIn](https://linkedin.com/in/testuser)
    """

    result = await parser.parse(readme_content)

    assert result["linkedin_username"] == "testuser"
    assert result["contact_sources"]["linkedin_username"] == "readme"


@pytest.mark.asyncio
async def test_parse_readme_with_twitter_link():
    """
    Test: Extract Twitter username from README
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    Follow me on Twitter: [@testuser](https://twitter.com/testuser)
    """

    result = await parser.parse(readme_content)

    assert result["twitter_username"] == "testuser"
    assert result["contact_sources"]["twitter_username"] == "readme"


@pytest.mark.asyncio
async def test_parse_readme_with_email():
    """
    Test: Extract email from README
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Contact Me

    Email: test@gmail.com
    """

    result = await parser.parse(readme_content)

    assert "test@gmail.com" in result["emails"]
    assert result["contact_sources"]["emails"] == "readme"


@pytest.mark.asyncio
async def test_parse_readme_with_multiple_contacts():
    """
    Test: Extract multiple contact methods from README
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User - Software Engineer

    - 📧 Email: test@gmail.com
    - 💼 LinkedIn: https://linkedin.com/in/testuser
    - 🐦 Twitter: @testuser
    - 🌐 Website: https://testuser.com
    """

    result = await parser.parse(readme_content)

    assert "test@gmail.com" in result["emails"]
    assert result["linkedin_username"] == "testuser"
    assert result["twitter_username"] == "testuser"
    assert result["website"] == "https://testuser.com"


@pytest.mark.asyncio
async def test_parse_readme_filters_noreply_emails():
    """
    Test: Noreply emails in README are filtered
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    Email: noreply@github.com
    Real Email: test@gmail.com
    """

    result = await parser.parse(readme_content)

    # Only real email should be extracted
    assert "test@gmail.com" in result["emails"]
    assert "noreply@github.com" not in result["emails"]


@pytest.mark.asyncio
async def test_parse_readme_with_markdown_badges():
    """
    Test: Extract links from markdown badges
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    [![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue)](https://linkedin.com/in/testuser)
    [![Twitter](https://img.shields.io/badge/-Twitter-blue)](https://twitter.com/testuser)
    """

    result = await parser.parse(readme_content)

    assert result["linkedin_username"] == "testuser"
    assert result["twitter_username"] == "testuser"


@pytest.mark.asyncio
async def test_parse_readme_handles_empty_content():
    """
    Test: Empty README returns empty result
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    result = await parser.parse("")

    assert result["emails"] == []
    assert result["linkedin_username"] is None
    assert result["twitter_username"] is None


@pytest.mark.asyncio
async def test_parse_readme_with_x_dot_com_links():
    """
    Test: Extract username from x.com links (new Twitter domain)
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    Follow me: https://x.com/testuser
    """

    result = await parser.parse(readme_content)

    assert result["twitter_username"] == "testuser"


@pytest.mark.asyncio
async def test_parse_readme_extracts_blog_urls():
    """
    Test: Extract blog/website URLs from README
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    Check out my blog: https://testuser.dev
    """

    result = await parser.parse(readme_content)

    assert result["website"] == "https://testuser.dev"


@pytest.mark.asyncio
async def test_parse_readme_deduplicates_emails():
    """
    Test: Duplicate emails in README are deduplicated
    Expected: FAIL - ReadmeParser not implemented
    """
    from src.contact_enrichment.services.readme_parser import ReadmeParser

    parser = ReadmeParser(github_token="fake_token")

    readme_content = """
    # Test User

    Email: test@gmail.com
    Contact: test@gmail.com
    Reach me: test@gmail.com
    """

    result = await parser.parse(readme_content)

    # Should only return one instance
    assert len(result["emails"]) == 1
    assert "test@gmail.com" in result["emails"]
