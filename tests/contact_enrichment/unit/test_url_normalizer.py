"""
Unit Test: URL Normalization
Module 010: Contact Enrichment

Tests the URLNormalizer library's ability to extract usernames from social URLs.
These tests MUST FAIL initially (TDD).
"""

import pytest


def test_linkedin_url_extracts_username():
    """
    Test: LinkedIn URL extracts clean username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("https://linkedin.com/in/testuser")

    assert result == "testuser"


def test_linkedin_url_with_trailing_slash_extracts_username():
    """
    Test: LinkedIn URL with trailing slash extracts username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("https://linkedin.com/in/testuser/")

    assert result == "testuser"


def test_linkedin_url_without_https_extracts_username():
    """
    Test: LinkedIn URL without https:// extracts username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("linkedin.com/in/testuser")

    assert result == "testuser"


def test_twitter_url_extracts_username():
    """
    Test: Twitter URL extracts clean username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_twitter_username("https://twitter.com/testuser")

    assert result == "testuser"


def test_twitter_username_with_at_symbol_extracts_username():
    """
    Test: Twitter @username extracts username without @
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_twitter_username("@testuser")

    assert result == "testuser"


def test_x_dot_com_url_extracts_username():
    """
    Test: x.com URL (new Twitter domain) extracts username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_twitter_username("https://x.com/testuser")

    assert result == "testuser"


def test_plain_username_returns_as_is():
    """
    Test: Plain username (no URL) returns as-is
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("testuser")

    assert result == "testuser"


def test_linkedin_url_with_query_params_extracts_username():
    """
    Test: LinkedIn URL with query params extracts username
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("https://linkedin.com/in/testuser?trk=profile")

    assert result == "testuser"


def test_none_value_returns_none():
    """
    Test: None value returns None (defensive)
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username(None)

    assert result is None


def test_empty_string_returns_none():
    """
    Test: Empty string returns None (defensive)
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_twitter_username("")

    assert result is None


def test_www_prefix_is_handled():
    """
    Test: www. prefix is handled correctly
    Expected: FAIL - URLNormalizer not implemented
    """
    from src.contact_enrichment.lib.url_normalizer import URLNormalizer

    normalizer = URLNormalizer()
    result = normalizer.extract_linkedin_username("https://www.linkedin.com/in/testuser")

    assert result == "testuser"
