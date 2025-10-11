"""
Integration tests for RefinementStage (Stage 3 of outreach pipeline)

Tests quality validation with cliché detection, personalization scoring,
and verification of specific mentions and CTA clarity.
"""

import pytest
from unittest.mock import Mock

from src.outreach_generator.stages.refinement_stage import RefinementStage
from src.outreach_generator.cliche_detector import ClicheDetector
from src.outreach_generator.personalization_scorer import PersonalizationScorer


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, refined_message=None, should_fail=False):
        self.refined_message = refined_message
        self.should_fail = should_fail
        self.model = "gpt-4o-mini"
        self.call_count = 0

    def complete(self, prompt, max_tokens=500, temperature=0.5, json_mode=False):
        """Mock completion that returns refined message."""
        self.call_count += 1

        if self.should_fail:
            raise Exception("LLM API error")

        if self.refined_message:
            return self.refined_message

        # Default: just return a cleaned version
        return "Hi John, I noticed your redis-clone project. We're building distributed systems at TechCorp. $150k-$200k. Interested in chatting?"


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def detector():
    """Create ClicheDetector instance."""
    return ClicheDetector()


@pytest.fixture
def scorer():
    """Create PersonalizationScorer instance."""
    return PersonalizationScorer()


@pytest.fixture
def candidate():
    """Sample candidate data."""
    return {
        "github_username": "johndoe",
        "top_repos": [
            {"name": "redis-clone", "description": "Distributed caching", "stars": 1200},
            {"name": "async-patterns", "description": "Async patterns", "stars": 850}
        ]
    }


@pytest.fixture
def enrichment():
    """Sample enrichment data."""
    return {
        "primary_email": "john@example.com",
        "linkedin_username": "johndoe",
        "company": "CurrentCorp"
    }


@pytest.fixture
def insights():
    """Sample analysis insights."""
    return {
        "achievements": ["Built redis-clone with 1200 stars"],
        "passion_areas": ["Distributed Systems"],
        "conversation_starters": ["Your redis-clone's concurrent write handling"]
    }


# ============================================================================
# Tests: Cliché Detection and Removal
# ============================================================================

def test_refine_detects_and_removes_cliches(detector, scorer, candidate, enrichment, insights):
    """Test that refinement detects and removes clichés."""
    message = {
        "message_text": "I'm reaching out about a great opportunity at TechCorp with our passionate team!",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)  # No LLM
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify clichés detected
    assert len(refined["cliches_removed"]) > 0
    assert "reaching out" in refined["cliches_removed"]
    assert "great opportunity" in refined["cliches_removed"]

    # Verify clichés removed from message
    assert "reaching out" not in refined["message_text"].lower()
    assert "great opportunity" not in refined["message_text"].lower()


def test_refine_with_no_cliches_returns_original(detector, scorer, candidate, enrichment, insights):
    """Test that clean message without clichés is returned unchanged."""
    message = {
        "message_text": "Hi John, I noticed your redis-clone's concurrent write handling. We're building distributed systems at TechCorp. $150k-$200k. Interested?",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify no clichés detected
    assert refined["cliches_removed"] == []

    # Verify message unchanged
    assert refined["message_text"] == message["message_text"]


# ============================================================================
# Tests: Specific Mention Verification
# ============================================================================

def test_refine_verifies_specific_repo_mention(detector, scorer, candidate, enrichment, insights):
    """Test that refinement verifies specific repo mentions."""
    message = {
        "message_text": "Hi John, your redis-clone project is impressive. We need distributed systems expertise. $150k-$200k.",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify specific mention detected
    assert refined["specific_mention_verified"] is True


def test_refine_flags_missing_specific_mention(detector, scorer, candidate, enrichment, insights):
    """Test that missing specific repo mention is flagged."""
    message = {
        "message_text": "Hi John, your GitHub work is impressive. We're hiring at TechCorp. $150k-$200k.",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify no specific mention
    assert refined["specific_mention_verified"] is False
    assert "no_specific_repo_mention" in refined["quality_flags"]


# ============================================================================
# Tests: CTA Clarity Verification
# ============================================================================

def test_refine_verifies_clear_cta(detector, scorer, candidate, enrichment, insights):
    """Test that clear CTA is verified."""
    message = {
        "message_text": "Hi John, your redis-clone is great. We're hiring. $150k-$200k. Interested in chatting?",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify CTA clarity
    assert refined["cta_clarity_verified"] is True


def test_refine_flags_unclear_cta(detector, scorer, candidate, enrichment, insights):
    """Test that unclear CTA is flagged."""
    message = {
        "message_text": "Hi John, your redis-clone is impressive. We're building distributed systems at TechCorp.",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify no clear CTA
    assert refined["cta_clarity_verified"] is False
    assert "unclear_cta" in refined["quality_flags"]


def test_refine_verifies_cta_with_link(detector, scorer, candidate, enrichment, insights):
    """Test that CTA with link is verified."""
    message = {
        "message_text": "Hi John, your redis-clone is great. Check out https://calendly.com/me for a chat.",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify CTA with link
    assert refined["cta_clarity_verified"] is True


# ============================================================================
# Tests: Personalization Scoring
# ============================================================================

def test_refine_calculates_personalization_score(detector, scorer, candidate, enrichment, insights):
    """Test that refinement calculates personalization score."""
    message = {
        "message_text": "Hi John, your redis-clone's concurrent write handling is exactly what we need at TechCorp. $150k-$200k. Chat?",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify score calculated
    assert "personalization_score" in refined
    assert isinstance(refined["personalization_score"], float)
    assert refined["personalization_score"] >= 0
    assert refined["personalization_score"] <= 100

    # Verify breakdown present
    assert "personalization_breakdown" in refined
    assert "repo_mention" in refined["personalization_breakdown"]


def test_refine_flags_low_personalization_score(detector, scorer, candidate, enrichment, insights):
    """Test that low personalization score (<70) is flagged."""
    message = {
        "message_text": "Hi there, we have an opportunity at our company. Interested?",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify low score flagged
    assert refined["personalization_score"] < 70
    assert "low_personalization" in refined["quality_flags"]


def test_refine_high_personalization_no_flags(detector, scorer, candidate, enrichment, insights):
    """Test that high personalization score has no quality flags."""
    message = {
        "message_text": "Hi John, your redis-clone's distributed caching with concurrent writes is exactly our approach at TechCorp. Senior Backend $150k-$200k. Interested in chatting?",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify high score
    assert refined["personalization_score"] >= 70

    # Should have minimal or no quality flags
    assert "low_personalization" not in refined["quality_flags"]
    assert "no_specific_repo_mention" not in refined["quality_flags"]
    assert "unclear_cta" not in refined["quality_flags"]


# ============================================================================
# Tests: LLM Refinement
# ============================================================================

def test_refine_with_llm_uses_intelligent_refinement(detector, scorer, candidate, enrichment, insights):
    """Test that refinement with LLM uses intelligent refinement."""
    message = {
        "message_text": "I'm reaching out about a great opportunity with our passionate team!",
        "channel": "email"
    }

    refined_by_llm = "Hi John, we're hiring for distributed systems at TechCorp. $150k-$200k. Interested?"
    mock_llm = MockLLMClient(refined_message=refined_by_llm)

    stage = RefinementStage(mock_llm, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify LLM was called
    assert mock_llm.call_count == 1

    # Verify refined message from LLM
    assert refined["message_text"] == refined_by_llm

    # Verify tokens tracked
    assert refined["tokens_used"] > 0


def test_refine_with_llm_failure_falls_back_to_simple_removal(detector, scorer, candidate, enrichment, insights):
    """Test that LLM failure falls back to simple cliché removal."""
    message = {
        "message_text": "I'm reaching out about a great opportunity.",
        "channel": "email"
    }

    mock_llm = MockLLMClient(should_fail=True)

    stage = RefinementStage(mock_llm, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify clichés still removed (via fallback)
    assert "reaching out" not in refined["message_text"].lower()
    assert "great opportunity" not in refined["message_text"].lower()

    # Verify tokens = 0 (LLM failed)
    assert refined["tokens_used"] == 0


# ============================================================================
# Tests: Full Refinement Pipeline
# ============================================================================

def test_refine_full_pipeline_with_all_checks(detector, scorer, candidate, enrichment, insights):
    """Test full refinement pipeline with all quality checks."""
    message = {
        "message_text": "I'm reaching out about your redis-clone's concurrent handling. We're at TechCorp building distributed systems. $150k-$200k. Chat?",
        "subject_line": "Redis expertise needed at TechCorp",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify all components present
    assert "message_text" in refined
    assert "subject_line" in refined
    assert "channel" in refined
    assert "cliches_removed" in refined
    assert "personalization_score" in refined
    assert "personalization_breakdown" in refined
    assert "quality_flags" in refined
    assert "specific_mention_verified" in refined
    assert "cta_clarity_verified" in refined
    assert "tokens_used" in refined

    # Verify clichés detected and removed
    assert "reaching out" in refined["cliches_removed"]
    assert "reaching out" not in refined["message_text"].lower()

    # Verify verifications
    assert refined["specific_mention_verified"] is True  # redis-clone mentioned
    assert refined["cta_clarity_verified"] is True  # "Chat?" present

    # Verify score calculated
    assert refined["personalization_score"] > 0


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_refine_empty_message(detector, scorer, candidate, enrichment, insights):
    """Test refinement of empty message."""
    message = {
        "message_text": "",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Should handle gracefully
    assert refined["message_text"] == ""
    assert refined["cliches_removed"] == []
    assert refined["specific_mention_verified"] is False
    assert refined["cta_clarity_verified"] is False


def test_refine_preserves_subject_line(detector, scorer, candidate, enrichment, insights):
    """Test that refinement preserves subject line."""
    message = {
        "message_text": "Hi John, your redis-clone is great. Chat?",
        "subject_line": "Redis expertise at TechCorp",
        "channel": "email"
    }

    stage = RefinementStage(None, detector, scorer)
    refined = stage.refine(message, candidate, enrichment, insights)

    # Verify subject preserved
    assert refined["subject_line"] == message["subject_line"]
