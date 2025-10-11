"""
Integration tests for ChannelOptimizer

Tests channel-specific validation and formatting logic for:
- Email (50-125 words, subject 36-50 chars)
- LinkedIn (<400 chars, 3-4 sentences)
- Twitter (<280 chars, 2-3 sentences)
"""

import pytest
from src.outreach_generator.channel_optimizer import ChannelOptimizer
from src.outreach_generator.models import ChannelType


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def optimizer():
    """Create ChannelOptimizer instance."""
    return ChannelOptimizer()


# ============================================================================
# Email Validation Tests
# ============================================================================

def test_valid_email_passes_validation(optimizer):
    """Test that valid email (subject 36-50 chars, body 50-125 words) validates successfully."""
    subject = "Senior Backend Engineer - Redis Expert at TechCorp"  # 50 chars
    body = " ".join(["word"] * 100)  # 100 words

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is True
    assert result["validation_errors"] == []
    assert result["channel"] == "email"
    assert result["subject_line"] == subject
    assert result["message_text"] == body


def test_email_with_short_subject_fails_validation(optimizer):
    """Test that email with subject <36 chars fails validation."""
    subject = "Great opportunity at TechCorp"  # 29 chars (too short)
    body = " ".join(["word"] * 100)  # 100 words (valid)

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) == 1
    assert "Subject line must be 36-50 characters" in result["validation_errors"][0]
    assert "(got 29)" in result["validation_errors"][0]


def test_email_with_long_subject_fails_validation(optimizer):
    """Test that email with subject >50 chars fails validation."""
    subject = "This is an incredibly long email subject line that exceeds the maximum allowed character limit"  # 94 chars
    body = " ".join(["word"] * 100)  # 100 words (valid)

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) == 1
    assert "Subject line must be 36-50 characters" in result["validation_errors"][0]
    assert "(got 94)" in result["validation_errors"][0]


def test_email_with_short_body_fails_validation(optimizer):
    """Test that email with body <50 words fails validation."""
    subject = "Senior Backend Engineer - Redis Expert needed"  # 46 chars (valid)
    body = " ".join(["word"] * 30)  # 30 words (too short)

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) == 1
    assert "Email body must be 50-125 words" in result["validation_errors"][0]
    assert "(got 30)" in result["validation_errors"][0]


def test_email_with_long_body_fails_validation(optimizer):
    """Test that email with body >125 words fails validation."""
    subject = "Senior Backend Engineer - Redis Expert needed"  # 46 chars (valid)
    body = " ".join(["word"] * 150)  # 150 words (too long)

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) == 1
    assert "Email body must be 50-125 words" in result["validation_errors"][0]
    assert "(got 150)" in result["validation_errors"][0]


def test_email_with_multiple_validation_errors(optimizer):
    """Test that email with multiple errors returns all errors."""
    subject = "Short"  # 5 chars (too short)
    body = " ".join(["word"] * 30)  # 30 words (too short)

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) == 2
    assert any("Subject line" in err for err in result["validation_errors"])
    assert any("Email body" in err for err in result["validation_errors"])


# ============================================================================
# LinkedIn Validation Tests
# ============================================================================

def test_valid_linkedin_passes_validation(optimizer):
    """Test that valid LinkedIn message (350 chars, 4 sentences) validates."""
    message = "Hi John, I noticed your redis-clone project with 1200 stars implementing distributed caching! We're building a similar system at TechCorp and need that exact expertise. Senior Backend Engineer role $150k-$200k fully remote. Interested in chatting?"  # ~250 chars, 4 sentences

    result = optimizer.format_for_linkedin(message)

    assert result["is_valid"] is True
    assert result["validation_errors"] == []
    assert result["channel"] == "linkedin"
    assert result["message_text"] == message


def test_linkedin_with_long_message_fails_validation(optimizer):
    """Test that LinkedIn message >400 chars fails validation."""
    message = "A" * 450  # 450 chars (too long)

    result = optimizer.format_for_linkedin(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("LinkedIn message must be <400 characters" in err for err in result["validation_errors"])
    assert "(got 450)" in result["validation_errors"][0]


def test_linkedin_with_too_few_sentences_fails_validation(optimizer):
    """Test that LinkedIn message with <3 sentences fails validation."""
    message = "Hi John! I saw your redis-clone project"  # 2 sentences (too few)

    result = optimizer.format_for_linkedin(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("LinkedIn message should have 3-4 sentences" in err for err in result["validation_errors"])


def test_linkedin_with_too_many_sentences_fails_validation(optimizer):
    """Test that LinkedIn message with >4 sentences fails validation."""
    message = "Hi John! I saw your project. We're hiring. Role is remote. Salary $150k. Interested?"  # 6 sentences

    result = optimizer.format_for_linkedin(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("LinkedIn message should have 3-4 sentences" in err for err in result["validation_errors"])


# ============================================================================
# Twitter Validation Tests
# ============================================================================

def test_valid_twitter_passes_validation(optimizer):
    """Test that valid Twitter message (250 chars, 3 sentences) validates."""
    message = "Loved your redis-clone project! We're hiring for a distributed systems role at TechCorp, $150k-$200k. Interested in chatting?"  # ~133 chars, 3 sentences

    result = optimizer.format_for_twitter(message)

    assert result["is_valid"] is True
    assert result["validation_errors"] == []
    assert result["channel"] == "twitter"
    assert result["message_text"] == message


def test_twitter_with_long_message_fails_validation(optimizer):
    """Test that Twitter message >280 chars fails validation."""
    message = "A" * 300  # 300 chars (too long)

    result = optimizer.format_for_twitter(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("Twitter message must be <280 characters" in err for err in result["validation_errors"])
    assert "(got 300)" in result["validation_errors"][0]


def test_twitter_with_too_few_sentences_fails_validation(optimizer):
    """Test that Twitter message with <2 sentences fails validation."""
    message = "Loved your redis-clone project"  # 1 sentence (too few)

    result = optimizer.format_for_twitter(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("Twitter message should have 2-3 sentences" in err for err in result["validation_errors"])


def test_twitter_with_too_many_sentences_fails_validation(optimizer):
    """Test that Twitter message with >3 sentences fails validation."""
    message = "Hi John! Saw your project. We're hiring. Role is remote. Interested?"  # 5 sentences

    result = optimizer.format_for_twitter(message)

    assert result["is_valid"] is False
    assert len(result["validation_errors"]) >= 1
    assert any("Twitter message should have 2-3 sentences" in err for err in result["validation_errors"])


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_email_with_exact_minimum_constraints_passes(optimizer):
    """Test email with exact minimum constraints (subject 36 chars, body 50 words)."""
    subject = "A" * 36  # Exactly 36 chars
    body = " ".join(["word"] * 50)  # Exactly 50 words

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is True


def test_email_with_exact_maximum_constraints_passes(optimizer):
    """Test email with exact maximum constraints (subject 50 chars, body 125 words)."""
    subject = "A" * 50  # Exactly 50 chars
    body = " ".join(["word"] * 125)  # Exactly 125 words

    result = optimizer.format_for_email(subject, body)

    assert result["is_valid"] is True


def test_linkedin_with_exact_399_chars_passes(optimizer):
    """Test LinkedIn with exactly 399 chars (just under limit)."""
    message = "A" * 396 + "..."  # 399 chars with 3 sentences

    result = optimizer.format_for_linkedin(message)

    # Should pass character limit but may fail sentence count
    assert not any("must be <400 characters" in err for err in result["validation_errors"])


def test_twitter_with_exact_279_chars_passes(optimizer):
    """Test Twitter with exactly 279 chars (just under limit)."""
    message = "A" * 277 + ".."  # 279 chars with 2 sentences

    result = optimizer.format_for_twitter(message)

    # Should pass character limit but may fail sentence count
    assert not any("must be <280 characters" in err for err in result["validation_errors"])
