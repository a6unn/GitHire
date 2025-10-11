"""
Integration tests for FollowUpGenerator

Tests the complete follow-up sequence generation:
- Day 3 (Reminder): Different repo mention
- Day 7 (Technical Challenge): Technical problem preview
- Day 14 (Soft Close): Gentle opt-out option
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.outreach_generator.follow_up_generator import FollowUpGenerator
from src.outreach_generator.models import OutreachMessage, ChannelType, PersonalizationMetadata, FollowUpAngle


# ============================================================================
# Mock LLM Client
# ============================================================================

class MockLLMClient:
    """Mock LLM client for testing follow-up generation."""

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.call_count = 0
        self.last_prompt = None

    def complete(self, prompt, max_tokens=300, temperature=0.7, json_mode=False):
        """Mock completion that returns different responses based on prompt."""
        self.call_count += 1
        self.last_prompt = prompt

        prompt_lower = prompt.lower()

        # Day 3 Reminder (mentions different repo)
        if "day 3 reminder" in prompt_lower or "brief follow-up" in prompt_lower:
            return "Hi John, saw your async-patterns library too - clean abstraction design. Still exploring the Senior Backend role ($150k-$200k)? Quick chat this week?"

        # Day 7 Technical Challenge
        elif "day 7" in prompt_lower or "technical challenge" in prompt_lower:
            return "Hi John, thought you'd find this interesting: we're wrestling with distributed lock management across 20+ Redis instances (handling 10M writes/sec). Your redis-clone experience seems directly applicable. Want to discuss our approach? $150k-$200k + equity."

        # Day 14 Soft Close
        elif "day 14" in prompt_lower or "soft close" in prompt_lower or "final" in prompt_lower:
            return "Hi John, assuming the Senior Backend role isn't a fit right now - no worries! If you'd like me to stop reaching out, just let me know. Otherwise, I'll keep you in mind for future roles."

        # Default
        return "Follow-up message"


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def outreach_message():
    """Sample outreach message."""
    metadata = PersonalizationMetadata(
        referenced_repositories=["redis-clone"],
        technical_details_mentioned=["concurrent writes", "distributed caching"],
        enrichment_data_used={"email": "john@example.com"},
        analysis_insights={
            "achievements": ["Built redis-clone with 1200 stars"],
            "passion_areas": ["Distributed Systems"],
            "career_trajectory": "Senior to Staff Engineer path",
            "minimal_data_fallback": False
        },
        cliches_removed=[],
        quality_flags=[]
    )

    return OutreachMessage(
        shortlist_id="candidate_johndoe",
        channel=ChannelType.EMAIL,
        subject_line="Redis expertise needed for distributed systems",
        message_text="Hi John, I noticed your redis-clone's concurrent write handling with locks. That's exactly our approach for caching at TechCorp. We're building a real-time analytics platform processing 10M events/sec. Need your distributed systems expertise. Senior Backend Engineer role, $150k-$200k, fully remote. Interested in a quick chat this week?",
        personalization_score=85.0,
        personalization_metadata=metadata,
        tokens_used=450,
        stage_breakdown={"analysis": 150, "generation": 200, "refinement": 100, "total": 450},
        is_edited=False,
        generated_at=datetime.utcnow()
    )


@pytest.fixture
def candidate():
    """Sample candidate data."""
    return {
        "github_username": "johndoe",
        "name": "John Doe",
        "top_repos": [
            {"name": "redis-clone", "description": "Distributed caching", "stars": 1200},
            {"name": "async-patterns", "description": "Async patterns library", "stars": 850},
            {"name": "websocket-server", "description": "WebSocket server", "stars": 500}
        ],
        "total_repos": 15,
        "contribution_count": 1500
    }


@pytest.fixture
def job_req():
    """Sample job requirements."""
    return {
        "role_type": "Senior Backend Engineer",
        "company_name": "TechCorp",
        "salary_range": "$150,000 - $200,000",
        "required_skills": ["Python", "Redis", "Distributed Systems"],
        "tech_stack": ["Python", "Redis", "Kafka"]
    }


# ============================================================================
# Tests: Single Follow-Up Generation
# ============================================================================

def test_generate_reminder_followup(mock_llm, outreach_message, candidate, job_req):
    """Test Day 3 reminder follow-up generation."""
    generator = FollowUpGenerator(mock_llm)

    # Generate Day 3 reminder
    reminder = generator._generate_single_followup(
        outreach_message=outreach_message,
        job_req=job_req,
        candidate=candidate,
        sequence_num=1,
        scheduled_days_after=3,
        angle=FollowUpAngle.REMINDER
    )

    # Verify structure
    assert reminder.sequence_number == 1
    assert reminder.scheduled_days_after == 3
    assert reminder.angle == FollowUpAngle.REMINDER
    assert reminder.outreach_message_id == "candidate_johndoe"

    # Verify content mentions different repo
    assert "async-patterns" in reminder.message_text or "websocket" in reminder.message_text.lower()

    # Verify brief (should be ~30-50 words)
    word_count = len(reminder.message_text.split())
    assert word_count < 80  # Allow some flexibility


def test_generate_technical_challenge_followup(mock_llm, outreach_message, candidate, job_req):
    """Test Day 7 technical challenge follow-up generation."""
    generator = FollowUpGenerator(mock_llm)

    # Generate Day 7 technical challenge
    challenge = generator._generate_single_followup(
        outreach_message=outreach_message,
        job_req=job_req,
        candidate=candidate,
        sequence_num=2,
        scheduled_days_after=7,
        angle=FollowUpAngle.TECHNICAL_CHALLENGE
    )

    # Verify structure
    assert challenge.sequence_number == 2
    assert challenge.scheduled_days_after == 7
    assert challenge.angle == FollowUpAngle.TECHNICAL_CHALLENGE

    # Verify content mentions technical problem
    assert "distributed" in challenge.message_text.lower() or "redis" in challenge.message_text.lower()


def test_generate_soft_close_followup(mock_llm, outreach_message, candidate, job_req):
    """Test Day 14 soft close follow-up generation."""
    generator = FollowUpGenerator(mock_llm)

    # Generate Day 14 soft close
    soft_close = generator._generate_single_followup(
        outreach_message=outreach_message,
        job_req=job_req,
        candidate=candidate,
        sequence_num=3,
        scheduled_days_after=14,
        angle=FollowUpAngle.SOFT_CLOSE
    )

    # Verify structure
    assert soft_close.sequence_number == 3
    assert soft_close.scheduled_days_after == 14
    assert soft_close.angle == FollowUpAngle.SOFT_CLOSE

    # Verify content is a soft close (no pressure, opt-out option)
    message_lower = soft_close.message_text.lower()
    assert "no worries" in message_lower or "no problem" in message_lower or "totally fine" in message_lower


# ============================================================================
# Tests: Full Sequence Generation
# ============================================================================

def test_generate_full_sequence(mock_llm, outreach_message, candidate, job_req):
    """Test generating full 3-part follow-up sequence."""
    generator = FollowUpGenerator(mock_llm)

    # Generate full sequence
    follow_ups = generator.generate_sequence(outreach_message, job_req, candidate)

    # Verify 3 follow-ups generated
    assert len(follow_ups) == 3

    # Verify sequence numbers
    assert follow_ups[0].sequence_number == 1
    assert follow_ups[1].sequence_number == 2
    assert follow_ups[2].sequence_number == 3

    # Verify scheduled days
    assert follow_ups[0].scheduled_days_after == 3
    assert follow_ups[1].scheduled_days_after == 7
    assert follow_ups[2].scheduled_days_after == 14

    # Verify angles
    assert follow_ups[0].angle == FollowUpAngle.REMINDER
    assert follow_ups[1].angle == FollowUpAngle.TECHNICAL_CHALLENGE
    assert follow_ups[2].angle == FollowUpAngle.SOFT_CLOSE

    # Verify LLM called 3 times
    assert mock_llm.call_count == 3


def test_generate_sequence_no_repetition(mock_llm, outreach_message, candidate, job_req):
    """Test that follow-ups have unique content (no repetition)."""
    generator = FollowUpGenerator(mock_llm)

    follow_ups = generator.generate_sequence(outreach_message, job_req, candidate)

    # Verify all messages are different
    messages = [f.message_text for f in follow_ups]
    assert messages[0] != messages[1]
    assert messages[1] != messages[2]
    assert messages[0] != messages[2]


def test_generate_sequence_preserves_context(mock_llm, outreach_message, candidate, job_req):
    """Test that follow-ups preserve original context."""
    generator = FollowUpGenerator(mock_llm)

    follow_ups = generator.generate_sequence(outreach_message, job_req, candidate)

    # Verify all follow-ups reference the same role/company
    for followup in follow_ups:
        # Should mention role or company or salary
        message_lower = followup.message_text.lower()
        has_context = (
            "senior backend" in message_lower or
            "techcorp" in message_lower or
            "$150" in followup.message_text or
            "150k" in message_lower
        )
        assert has_context


def test_generate_sequence_all_have_timestamps(mock_llm, outreach_message, candidate, job_req):
    """Test that all follow-ups have generated_at timestamps."""
    generator = FollowUpGenerator(mock_llm)

    follow_ups = generator.generate_sequence(outreach_message, job_req, candidate)

    # Verify timestamps
    for followup in follow_ups:
        assert followup.generated_at is not None
        assert isinstance(followup.generated_at, datetime)


# ============================================================================
# Tests: Edge Cases
# ============================================================================

def test_generate_sequence_with_minimal_candidate_data(mock_llm, job_req):
    """Test follow-up generation with minimal candidate data."""
    # Minimal candidate
    minimal_candidate = {
        "github_username": "minimaluser",
        "top_repos": [],
        "total_repos": 0
    }

    # Minimal outreach message
    metadata = PersonalizationMetadata(
        referenced_repositories=[],
        technical_details_mentioned=[],
        enrichment_data_used={},
        analysis_insights={},
        cliches_removed=[],
        quality_flags=[]
    )

    minimal_outreach = OutreachMessage(
        shortlist_id="candidate_minimaluser",
        channel=ChannelType.EMAIL,
        subject_line="Senior Backend Engineer opportunity at TechCorp",  # 46 chars
        message_text="Hi, we have a Senior Backend Engineer role at TechCorp. $150k-$200k. Interested?",
        personalization_score=40.0,
        personalization_metadata=metadata,
        tokens_used=100,
        stage_breakdown={"total": 100},
        is_edited=False,
        generated_at=datetime.utcnow()
    )

    generator = FollowUpGenerator(mock_llm)
    follow_ups = generator.generate_sequence(minimal_outreach, job_req, minimal_candidate)

    # Should still generate 3 follow-ups
    assert len(follow_ups) == 3


def test_generate_sequence_error_handling(candidate, job_req):
    """Test error handling when LLM fails."""
    # Mock LLM that always fails
    class FailingLLMClient:
        def complete(self, prompt, max_tokens=300, temperature=0.7, json_mode=False):
            raise Exception("LLM API error")

    failing_llm = FailingLLMClient()
    generator = FollowUpGenerator(failing_llm)

    # Minimal outreach message
    metadata = PersonalizationMetadata(
        referenced_repositories=[],
        technical_details_mentioned=[],
        enrichment_data_used={},
        analysis_insights={},
        cliches_removed=[],
        quality_flags=[]
    )

    outreach = OutreachMessage(
        shortlist_id="candidate_test",
        channel=ChannelType.EMAIL,
        subject_line="Backend Engineer opportunity at test company",  # 44 chars
        message_text="Test message for error handling verification in follow-up generation",
        personalization_score=50.0,
        personalization_metadata=metadata,
        tokens_used=100,
        stage_breakdown={"total": 100},
        is_edited=False,
        generated_at=datetime.utcnow()
    )

    # Should handle error gracefully
    follow_ups = generator.generate_sequence(outreach, job_req, candidate)

    # Should return 3 follow-ups with error messages
    assert len(follow_ups) == 3
    for followup in follow_ups:
        assert "[Error generating follow-up]" in followup.message_text
