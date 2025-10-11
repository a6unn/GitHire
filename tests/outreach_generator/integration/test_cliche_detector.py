"""
Integration tests for ClicheDetector

Tests detection and removal of common recruiter clichés.
"""

import pytest
from src.outreach_generator.cliche_detector import ClicheDetector


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def detector():
    """Create ClicheDetector instance."""
    return ClicheDetector()


# ============================================================================
# Tests: Cliché Detection
# ============================================================================

def test_detect_reaching_out_cliche(detector):
    """Test detection of 'reaching out' cliché."""
    message = "I'm reaching out to discuss an opportunity at TechCorp."

    cliches = detector.detect(message)

    assert "reaching out" in cliches


def test_detect_great_opportunity_cliche(detector):
    """Test detection of 'great opportunity' cliché."""
    message = "We have a great opportunity for a Senior Backend Engineer."

    cliches = detector.detect(message)

    assert "great opportunity" in cliches


def test_detect_multiple_cliches(detector):
    """Test detection of multiple clichés in one message."""
    message = "I'm reaching out about a great opportunity with our passionate team working on cutting-edge technology!"

    cliches = detector.detect(message)

    assert "reaching out" in cliches
    assert "great opportunity" in cliches
    assert "passionate team" in cliches
    assert "cutting-edge" in cliches
    assert len(cliches) >= 4


def test_detect_no_cliches_in_clean_message(detector):
    """Test that clean message with no clichés returns empty list."""
    message = "Hi John, I noticed your redis-clone project with 1200 stars. We're building a similar distributed system at TechCorp. $150k-$200k. Interested?"

    cliches = detector.detect(message)

    assert cliches == []


def test_detect_case_insensitive(detector):
    """Test that detection is case-insensitive."""
    message = "I'm REACHING OUT about a GREAT OPPORTUNITY."

    cliches = detector.detect(message)

    assert "reaching out" in cliches
    assert "great opportunity" in cliches


def test_detect_word_boundary_matching(detector):
    """Test that detection uses word boundaries (not partial matches)."""
    # "researching" should NOT match "reaching"
    message = "I've been researching your background and outperforming expectations."

    cliches = detector.detect(message)

    # Should not detect "reaching" as part of "researching"
    assert "reaching out" not in cliches


# ============================================================================
# Tests: Cliché Removal
# ============================================================================

def test_remove_reaching_out_cliche(detector):
    """Test removal of 'reaching out' cliché."""
    message = "I'm reaching out to discuss an opportunity."

    cleaned, removed = detector.remove(message)

    assert "reaching out" not in cleaned.lower()
    assert "contacting you" in cleaned.lower() or "contact" in cleaned.lower()
    assert "reaching out" in removed


def test_remove_great_opportunity_cliche(detector):
    """Test removal of 'great opportunity' cliché."""
    message = "We have a great opportunity for you."

    cleaned, removed = detector.remove(message)

    assert "great opportunity" not in cleaned.lower()
    assert "opportunity" in cleaned.lower()  # Should keep "opportunity" part
    assert "great opportunity" in removed


def test_remove_multiple_cliches(detector):
    """Test removal of multiple clichés."""
    message = "I'm reaching out about a great opportunity with our passionate team!"

    cleaned, removed = detector.remove(message)

    # Verify all clichés removed
    assert "reaching out" not in cleaned.lower()
    assert "great opportunity" not in cleaned.lower()
    assert "passionate team" not in cleaned.lower()

    # Verify removed list
    assert len(removed) >= 3
    assert "reaching out" in removed
    assert "great opportunity" in removed
    assert "passionate team" in removed


def test_remove_preserves_message_meaning(detector):
    """Test that removal preserves overall message meaning."""
    message = "I'm reaching out about a great opportunity at TechCorp. We need a Senior Backend Engineer."

    cleaned, removed = detector.remove(message)

    # Should still mention TechCorp and Senior Backend Engineer
    assert "TechCorp" in cleaned
    assert "Senior Backend Engineer" in cleaned
    assert len(cleaned) > 20  # Should still have substantial content


def test_remove_cleans_up_extra_spaces(detector):
    """Test that removal cleans up extra spaces."""
    message = "I'm   reaching out   about   a great opportunity."

    cleaned, removed = detector.remove(message)

    # Should not have multiple consecutive spaces
    assert "  " not in cleaned


def test_remove_returns_empty_list_for_clean_message(detector):
    """Test that clean message returns empty removed list."""
    message = "Hi John, your redis-clone's concurrent write handling is impressive!"

    cleaned, removed = detector.remove(message)

    assert cleaned == message  # Should be unchanged
    assert removed == []


# ============================================================================
# Tests: Specific Cliché Categories
# ============================================================================

def test_detect_corporate_buzzwords(detector):
    """Test detection of corporate buzzwords."""
    message = "We need synergy and thought leaders to move the needle."

    cliches = detector.detect(message)

    assert "synergy" in cliches
    assert "thought leader" in cliches or "move the needle" in cliches


def test_detect_tech_buzzwords(detector):
    """Test detection of tech buzzwords (without context)."""
    message = "We're a cutting-edge company using bleeding edge technology."

    cliches = detector.detect(message)

    assert "cutting-edge" in cliches or "bleeding edge" in cliches


def test_detect_team_culture_buzzwords(detector):
    """Test detection of team/culture buzzwords."""
    message = "Join our rockstar team of ninjas in a fast-paced environment where you'll wear many hats!"

    cliches = detector.detect(message)

    # Should detect at least some of these
    detected_count = sum([
        "rockstar" in cliches,
        "ninja" in cliches,
        "fast-paced environment" in cliches,
        "wear many hats" in cliches
    ])
    assert detected_count >= 2


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_detect_empty_message(detector):
    """Test detection on empty message."""
    message = ""

    cliches = detector.detect(message)

    assert cliches == []


def test_remove_empty_message(detector):
    """Test removal on empty message."""
    message = ""

    cleaned, removed = detector.remove(message)

    assert cleaned == ""
    assert removed == []


def test_detect_message_with_only_cliches(detector):
    """Test message consisting entirely of clichés."""
    message = "Great opportunity! Passionate team! Cutting-edge technology!"

    cliches = detector.detect(message)

    assert len(cliches) >= 3
