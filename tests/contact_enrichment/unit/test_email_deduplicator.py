"""
Unit Test: Email Deduplication
Module 010: Contact Enrichment

Tests the EmailDeduplicator library's ability to remove duplicates and prioritize emails.
These tests MUST FAIL initially (TDD).
"""

import pytest


def test_duplicate_emails_are_removed():
    """
    Test: Duplicate emails are removed from list
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = ["test@gmail.com", "test@gmail.com", "user@company.com"]
    result = deduplicator.deduplicate(emails)

    assert len(result) == 2
    assert "test@gmail.com" in result
    assert "user@company.com" in result


def test_case_insensitive_deduplication():
    """
    Test: Emails are deduplicated case-insensitively
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = ["Test@Gmail.com", "test@gmail.com", "TEST@GMAIL.COM"]
    result = deduplicator.deduplicate(emails)

    # Should return only one email, preserving original case of first occurrence
    assert len(result) == 1
    assert result[0].lower() == "test@gmail.com"


def test_noreply_emails_are_filtered_during_deduplication():
    """
    Test: Noreply emails are filtered out during deduplication
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = [
        "test@gmail.com",
        "123456+user@users.noreply.github.com",
        "user@company.com",
    ]
    result = deduplicator.deduplicate(emails)

    # Noreply should be filtered
    assert len(result) == 2
    assert "test@gmail.com" in result
    assert "user@company.com" in result
    assert "123456+user@users.noreply.github.com" not in result


def test_spam_domains_are_filtered_during_deduplication():
    """
    Test: Spam/test domains are filtered out during deduplication
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = ["test@gmail.com", "fake@example.com", "user@test.com"]
    result = deduplicator.deduplicate(emails)

    # example.com and test.com should be filtered
    assert len(result) == 1
    assert "test@gmail.com" in result
    assert "fake@example.com" not in result
    assert "user@test.com" not in result


def test_invalid_emails_are_filtered_during_deduplication():
    """
    Test: Invalid email formats are filtered during deduplication
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = ["test@gmail.com", "notanemail", "user@", "@domain.com"]
    result = deduplicator.deduplicate(emails)

    # Only valid email should remain
    assert len(result) == 1
    assert "test@gmail.com" in result


def test_empty_list_returns_empty_list():
    """
    Test: Empty list returns empty list
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    result = deduplicator.deduplicate([])

    assert result == []


def test_all_invalid_emails_returns_empty_list():
    """
    Test: List of all invalid emails returns empty list
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    emails = ["notanemail", "fake@example.com", "user@noreply.github.com"]
    result = deduplicator.deduplicate(emails)

    assert result == []


def test_prioritize_returns_best_email():
    """
    Test: Prioritize returns best email based on source quality
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()

    # Commit email should be prioritized over profile email
    emails_with_sources = [
        ("profile_email@gmail.com", "profile"),
        ("commit_email@gmail.com", "commit"),
    ]

    result = deduplicator.prioritize(emails_with_sources)

    # Commit email should be selected as primary
    assert result == "commit_email@gmail.com"


def test_prioritize_with_empty_list_returns_none():
    """
    Test: Prioritize with empty list returns None
    Expected: FAIL - EmailDeduplicator not implemented
    """
    from src.contact_enrichment.lib.email_deduplicator import EmailDeduplicator

    deduplicator = EmailDeduplicator()
    result = deduplicator.prioritize([])

    assert result is None
