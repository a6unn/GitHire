"""
Unit Test: Noreply Email Filtering
Module 010: Contact Enrichment

Tests the NoreplyFilter library's ability to detect privacy-protected emails.
These tests MUST FAIL initially (TDD).
"""

import pytest


def test_github_noreply_email_is_filtered():
    """
    Test: GitHub noreply email is detected and filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("123456+username@users.noreply.github.com")

    assert result is True


def test_standard_github_noreply_is_filtered():
    """
    Test: Standard GitHub noreply.github.com is filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("username@noreply.github.com")

    assert result is True


def test_generic_noreply_email_is_filtered():
    """
    Test: Generic noreply@ email is filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("noreply@example.com")

    assert result is True


def test_do_not_reply_pattern_is_filtered():
    """
    Test: do-not-reply pattern is filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("do-not-reply@company.com")

    assert result is True


def test_gitlab_noreply_is_filtered():
    """
    Test: GitLab noreply email is filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("user@noreply.gitlab.com")

    assert result is True


def test_real_email_is_not_filtered():
    """
    Test: Real email address is NOT filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("test@gmail.com")

    assert result is False


def test_notifications_email_is_filtered():
    """
    Test: notifications@ automated email is filtered
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("notifications@github.com")

    assert result is True


def test_none_value_returns_false():
    """
    Test: None value returns False (defensive)
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply(None)

    assert result is False


def test_empty_string_returns_false():
    """
    Test: Empty string returns False (defensive)
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("")

    assert result is False


def test_case_insensitive_noreply_detection():
    """
    Test: NoReply (mixed case) is detected case-insensitively
    Expected: FAIL - NoreplyFilter not implemented
    """
    from src.contact_enrichment.lib.noreply_filter import NoreplyFilter

    filter = NoreplyFilter()
    result = filter.is_noreply("NoReply@example.com")

    assert result is True
