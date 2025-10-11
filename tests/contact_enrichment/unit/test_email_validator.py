"""
Unit Test: Email Validation
Module 010: Contact Enrichment

Tests the EmailValidator library's ability to validate email formats.
These tests MUST FAIL initially (TDD).
"""

import pytest


def test_valid_email_passes_validation():
    """
    Test: Valid email "test@gmail.com" passes validation
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("test@gmail.com")

    assert result is True


def test_invalid_email_fails_validation():
    """
    Test: Invalid email "notanemail" fails validation
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("notanemail")

    assert result is False


def test_email_without_at_symbol_fails_validation():
    """
    Test: Email without @ symbol fails validation
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("testgmail.com")

    assert result is False


def test_email_without_domain_fails_validation():
    """
    Test: Email without domain fails validation
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("test@")

    assert result is False


def test_empty_string_returns_false():
    """
    Test: Empty string returns False
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("")

    assert result is False


def test_none_value_returns_false():
    """
    Test: None value returns False (defensive)
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate(None)

    assert result is False


def test_email_with_subdomain_is_valid():
    """
    Test: Email with subdomain passes validation
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("test@mail.example.com")

    assert result is True


def test_email_with_plus_addressing_is_valid():
    """
    Test: Email with + addressing (test+label@gmail.com) is valid
    Expected: FAIL - EmailValidator not implemented
    """
    from src.contact_enrichment.lib.email_validator import EmailValidator

    validator = EmailValidator()
    result = validator.validate("test+label@gmail.com")

    assert result is True
