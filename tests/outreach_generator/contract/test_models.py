"""
Contract tests for Outreach Generator data models.

Tests model validation, field constraints, and data integrity.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.outreach_generator.models import (
    ChannelType,
    FollowUpAngle,
    PersonalizationMetadata,
    OutreachMessage,
    FollowUpSequence,
)


# ============================================================================
# PersonalizationMetadata Tests
# ============================================================================

def test_personalization_metadata_valid_creation():
    """Test valid PersonalizationMetadata creation."""
    metadata = PersonalizationMetadata(
        referenced_repositories=["redis-clone", "async-patterns"],
        technical_details_mentioned=["concurrent writes", "async/await"],
        enrichment_data_used={"email": True, "linkedin": True},
        analysis_insights={"achievements": ["Built system"]},
        cliches_removed=["reaching out"],
        quality_flags=[]
    )

    assert len(metadata.referenced_repositories) == 2
    assert len(metadata.technical_details_mentioned) == 2
    assert metadata.enrichment_data_used["email"] is True
    assert len(metadata.cliches_removed) == 1
    assert len(metadata.quality_flags) == 0


def test_personalization_metadata_empty_lists():
    """Test PersonalizationMetadata with empty lists (should validate)."""
    metadata = PersonalizationMetadata()

    assert metadata.referenced_repositories == []
    assert metadata.technical_details_mentioned == []
    assert metadata.enrichment_data_used == {}
    assert metadata.analysis_insights == {}
    assert metadata.cliches_removed == []
    assert metadata.quality_flags == []


def test_personalization_metadata_with_populated_data():
    """Test PersonalizationMetadata with fully populated data."""
    metadata = PersonalizationMetadata(
        referenced_repositories=["repo1", "repo2", "repo3"],
        technical_details_mentioned=["feature1", "feature2"],
        enrichment_data_used={
            "email": True,
            "linkedin": True,
            "twitter": False,
            "blog": "https://example.com"
        },
        analysis_insights={
            "achievements": ["Achievement 1", "Achievement 2", "Achievement 3"],
            "passion_areas": ["AI/ML", "Systems Programming"],
            "trajectory": "Senior to Staff Engineer path",
            "starters": ["Starter 1", "Starter 2"]
        },
        cliches_removed=["reaching out", "great opportunity", "passionate team"],
        quality_flags=["low_personalization"]
    )

    assert len(metadata.referenced_repositories) == 3
    assert len(metadata.analysis_insights["achievements"]) == 3
    assert len(metadata.cliches_removed) == 3
    assert metadata.quality_flags[0] == "low_personalization"


# ============================================================================
# OutreachMessage Tests
# ============================================================================

def test_outreach_message_valid_email_creation():
    """Test valid OutreachMessage creation for email with subject_line."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.EMAIL,
        subject_line="Your redis-clone project + Backend @ Tech",  # 45 chars (36-50 valid)
        message_text="Hi Sarah, came across your redis-clone implementation...",
        personalization_score=85.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=1500,
        stage_breakdown={"analysis": 500, "generation": 700, "refinement": 300}
    )

    assert message.channel == ChannelType.EMAIL
    assert message.subject_line is not None
    assert len(message.subject_line) >= 36
    assert len(message.subject_line) <= 50
    assert message.personalization_score == 85.0
    assert message.tokens_used == 1500
    assert message.is_edited is False
    assert message.edited_at is None


def test_outreach_message_valid_linkedin_no_subject():
    """Test valid OutreachMessage for LinkedIn (no subject_line)."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.LINKEDIN,
        subject_line=None,  # LinkedIn doesn't have subject
        message_text="Hi Alex, noticed your microservices work...",
        personalization_score=78.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=1200
    )

    assert message.channel == ChannelType.LINKEDIN
    assert message.subject_line is None
    assert message.personalization_score == 78.0


def test_outreach_message_personalization_score_validation_low():
    """Test personalization_score validation (reject < 0)."""
    with pytest.raises(ValidationError) as exc_info:
        OutreachMessage(
            shortlist_id="12345",
            channel=ChannelType.EMAIL,
            subject_line="Your redis-clone project + Backend @ Tech",
            message_text="Test message",
            personalization_score=-10.0,  # Invalid: < 0
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=1000
        )

    assert "personalization_score" in str(exc_info.value)


def test_outreach_message_personalization_score_validation_high():
    """Test personalization_score validation (reject > 100)."""
    with pytest.raises(ValidationError) as exc_info:
        OutreachMessage(
            shortlist_id="12345",
            channel=ChannelType.EMAIL,
            subject_line="Your redis-clone project + Backend @ Tech",
            message_text="Test message",
            personalization_score=150.0,  # Invalid: > 100
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=1000
        )

    assert "personalization_score" in str(exc_info.value)


def test_outreach_message_subject_line_too_short():
    """Test email subject_line length validation (< 36 chars rejected)."""
    with pytest.raises(ValidationError) as exc_info:
        OutreachMessage(
            shortlist_id="12345",
            channel=ChannelType.EMAIL,
            subject_line="Short subject",  # 13 chars, < 36
            message_text="Test message",
            personalization_score=80.0,
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=1000
        )

    assert "subject line" in str(exc_info.value).lower()


def test_outreach_message_subject_line_too_long():
    """Test email subject_line length validation (> 50 chars rejected)."""
    with pytest.raises(ValidationError) as exc_info:
        OutreachMessage(
            shortlist_id="12345",
            channel=ChannelType.EMAIL,
            subject_line="This is a very long subject line that exceeds fifty characters",  # > 50
            message_text="Test message",
            personalization_score=80.0,
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=1000
        )

    assert "subject line" in str(exc_info.value).lower()


def test_outreach_message_channel_validation():
    """Test channel validation (only email/linkedin/twitter)."""
    # Valid channels
    for channel in [ChannelType.EMAIL, ChannelType.LINKEDIN, ChannelType.TWITTER]:
        message = OutreachMessage(
            shortlist_id="12345",
            channel=channel,
            subject_line="Your redis-clone project + Backend @ Tech" if channel == ChannelType.EMAIL else None,
            message_text="Test message",
            personalization_score=80.0,
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=1000
        )
        assert message.channel == channel


def test_outreach_message_tokens_used_non_negative():
    """Test tokens_used must be non-negative."""
    with pytest.raises(ValidationError) as exc_info:
        OutreachMessage(
            shortlist_id="12345",
            channel=ChannelType.EMAIL,
            subject_line="Your redis-clone project + Backend @ Tech",
            message_text="Test message",
            personalization_score=80.0,
            personalization_metadata=PersonalizationMetadata(),
            tokens_used=-100  # Invalid: negative
        )

    assert "tokens_used" in str(exc_info.value)


def test_outreach_message_stage_breakdown_structure():
    """Test stage_breakdown structure."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.EMAIL,
        subject_line="Your redis-clone project + Backend @ Tech",
        message_text="Test message",
        personalization_score=80.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=1500,
        stage_breakdown={"analysis": 500, "generation": 700, "refinement": 300}
    )

    assert "analysis" in message.stage_breakdown
    assert "generation" in message.stage_breakdown
    assert "refinement" in message.stage_breakdown
    assert sum(message.stage_breakdown.values()) == message.tokens_used


# ============================================================================
# FollowUpSequence Tests
# ============================================================================

def test_followup_sequence_valid_creation():
    """Test valid FollowUpSequence creation."""
    followup = FollowUpSequence(
        outreach_message_id="67890",
        sequence_number=1,
        scheduled_days_after=3,
        message_text="Quick follow-up on my previous message...",
        angle=FollowUpAngle.REMINDER
    )

    assert followup.sequence_number == 1
    assert followup.scheduled_days_after == 3
    assert followup.angle == FollowUpAngle.REMINDER
    assert isinstance(followup.generated_at, datetime)


def test_followup_sequence_number_validation_too_low():
    """Test sequence_number validation (< 1 rejected)."""
    with pytest.raises(ValidationError) as exc_info:
        FollowUpSequence(
            outreach_message_id="67890",
            sequence_number=0,  # Invalid: < 1
            scheduled_days_after=3,
            message_text="Test message",
            angle=FollowUpAngle.REMINDER
        )

    assert "sequence_number" in str(exc_info.value)


def test_followup_sequence_number_validation_too_high():
    """Test sequence_number validation (> 3 rejected)."""
    with pytest.raises(ValidationError) as exc_info:
        FollowUpSequence(
            outreach_message_id="67890",
            sequence_number=4,  # Invalid: > 3
            scheduled_days_after=3,
            message_text="Test message",
            angle=FollowUpAngle.REMINDER
        )

    assert "sequence_number" in str(exc_info.value)


def test_followup_scheduled_days_after_validation_invalid():
    """Test scheduled_days_after validation (must be 3, 7, or 14)."""
    with pytest.raises(ValidationError) as exc_info:
        FollowUpSequence(
            outreach_message_id="67890",
            sequence_number=1,
            scheduled_days_after=5,  # Invalid: not 3, 7, or 14
            message_text="Test message",
            angle=FollowUpAngle.REMINDER
        )

    assert "scheduled_days_after" in str(exc_info.value)


def test_followup_scheduled_days_after_validation_valid():
    """Test scheduled_days_after validation (3, 7, 14 all valid)."""
    for days in [3, 7, 14]:
        followup = FollowUpSequence(
            outreach_message_id="67890",
            sequence_number=1,
            scheduled_days_after=days,
            message_text="Test message",
            angle=FollowUpAngle.REMINDER
        )
        assert followup.scheduled_days_after == days


def test_followup_angle_validation():
    """Test angle validation (all FollowUpAngle values valid)."""
    angles = [
        FollowUpAngle.REMINDER,
        FollowUpAngle.TECHNICAL_CHALLENGE,
        FollowUpAngle.CAREER_GROWTH,
        FollowUpAngle.SOFT_CLOSE
    ]

    for angle in angles:
        followup = FollowUpSequence(
            outreach_message_id="67890",
            sequence_number=1,
            scheduled_days_after=3,
            message_text="Test message",
            angle=angle
        )
        assert followup.angle == angle


# ============================================================================
# Additional Edge Case Tests
# ============================================================================

def test_outreach_message_with_empty_message_text():
    """Test message with empty message_text (should validate - may be filled later)."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.EMAIL,
        subject_line="Your redis-clone project + Backend @ Tech",
        message_text="",  # Empty but valid
        personalization_score=50.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=0
    )

    assert message.message_text == ""
    assert message.tokens_used == 0


def test_outreach_message_with_fallback_applied():
    """Test message with fallback_applied=True (minimal data scenario)."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.EMAIL,
        subject_line="Backend Engineer opportunity at TechCorp",
        message_text="Generic message due to minimal candidate data",
        personalization_score=40.0,  # Low score due to minimal data
        personalization_metadata=PersonalizationMetadata(
            quality_flags=["low_personalization", "minimal_data"]
        ),
        tokens_used=800
    )

    assert message.personalization_score == 40.0
    assert len(message.personalization_metadata.quality_flags) == 2


def test_outreach_message_zero_tokens():
    """Test message with zero tokens_used (edge case)."""
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.TWITTER,
        message_text="Test message",
        personalization_score=70.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=0  # Zero tokens (valid)
    )

    assert message.tokens_used == 0


def test_outreach_message_is_edited_workflow():
    """Test is_edited flag and edited_at timestamp workflow."""
    # Initial message (not edited)
    message = OutreachMessage(
        shortlist_id="12345",
        channel=ChannelType.EMAIL,
        subject_line="Your redis-clone project + Backend @ Tech",
        message_text="Original message",
        personalization_score=85.0,
        personalization_metadata=PersonalizationMetadata(),
        tokens_used=1500
    )

    assert message.is_edited is False
    assert message.edited_at is None

    # Simulate editing (would be done in business logic)
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    message.message_text = "Edited message"

    assert message.is_edited is True
    assert message.edited_at is not None
    assert isinstance(message.edited_at, datetime)
