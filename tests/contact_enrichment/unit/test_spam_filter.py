"""
Unit Test: Spam Domain Filtering
Module 010: Contact Enrichment

Tests the SpamFilter library's ability to detect fake/test email domains.
These tests MUST FAIL initially (TDD).
"""

import pytest


def test_example_com_domain_is_filtered():
    """
    Test: example.com (RFC 2606) is detected as spam
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("test@example.com")

    assert result is True


def test_test_com_domain_is_filtered():
    """
    Test: test.com domain is detected as spam
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("user@test.com")

    assert result is True


def test_localhost_domain_is_filtered():
    """
    Test: localhost domain is detected as spam
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("test@localhost")

    assert result is True


def test_disposable_tempmail_is_filtered():
    """
    Test: Disposable tempmail.com is detected as spam
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("user@tempmail.com")

    assert result is True


def test_mailinator_disposable_is_filtered():
    """
    Test: Mailinator disposable email is filtered
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("test@mailinator.com")

    assert result is True


def test_real_gmail_is_not_filtered():
    """
    Test: Real gmail.com domain is NOT filtered
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("user@gmail.com")

    assert result is False


def test_real_company_domain_is_not_filtered():
    """
    Test: Real company domain is NOT filtered
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("employee@acme-corp.com")

    assert result is False


def test_invalid_invalid_domain_is_filtered():
    """
    Test: invalid.invalid placeholder domain is filtered
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("test@invalid.invalid")

    assert result is True


def test_dev_local_domain_is_filtered():
    """
    Test: dev.local development domain is filtered
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("user@dev.local")

    assert result is True


def test_none_value_returns_false():
    """
    Test: None value returns False (defensive)
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain(None)

    assert result is False


def test_empty_string_returns_false():
    """
    Test: Empty string returns False (defensive)
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("")

    assert result is False


def test_case_insensitive_spam_detection():
    """
    Test: EXAMPLE.COM (uppercase) is detected case-insensitively
    Expected: FAIL - SpamFilter not implemented
    """
    from src.contact_enrichment.lib.spam_filter import SpamFilter

    filter = SpamFilter()
    result = filter.is_spam_domain("test@EXAMPLE.COM")

    assert result is True
