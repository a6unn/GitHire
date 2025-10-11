"""Contract tests for Outreach Generator data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.outreach_generator.models import (
    OutreachMessage,
    PersonalizationMetadata,
    ToneStyle
)


class TestPersonalizationMetadata:
    """Test PersonalizationMetadata model validation."""

    def test_valid_metadata_creation(self):
        """Test creating valid PersonalizationMetadata."""
        metadata = PersonalizationMetadata(
            referenced_repositories=["repo1", "repo2"],
            referenced_skills=["Python", "Docker"],
            tone_adjustment_reason="Top candidate, deep analysis",
            diversity_score=85.5
        )

        assert metadata.referenced_repositories == ["repo1", "repo2"]
        assert metadata.referenced_skills == ["Python", "Docker"]
        assert metadata.tone_adjustment_reason == "Top candidate, deep analysis"
        assert metadata.diversity_score == 85.5

    def test_default_values(self):
        """Test default values for optional fields."""
        metadata = PersonalizationMetadata()

        assert metadata.referenced_repositories == []
        assert metadata.referenced_skills == []
        assert metadata.tone_adjustment_reason == ""
        assert metadata.diversity_score == 100.0

    def test_diversity_score_validation_too_low(self):
        """Test diversity_score must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            PersonalizationMetadata(diversity_score=-1.0)

        assert "greater_than_equal" in str(exc_info.value)

    def test_diversity_score_validation_too_high(self):
        """Test diversity_score must be <= 100."""
        with pytest.raises(ValidationError) as exc_info:
            PersonalizationMetadata(diversity_score=101.0)

        assert "less_than_equal" in str(exc_info.value)

    def test_empty_lists_allowed(self):
        """Test empty lists are valid for repo and skill references."""
        metadata = PersonalizationMetadata(
            referenced_repositories=[],
            referenced_skills=[]
        )

        assert metadata.referenced_repositories == []
        assert metadata.referenced_skills == []


class TestOutreachMessage:
    """Test OutreachMessage model validation."""

    def test_valid_message_creation(self):
        """Test creating valid OutreachMessage."""
        metadata = PersonalizationMetadata(
            referenced_repositories=["awesome-project"],
            referenced_skills=["Python", "FastAPI"]
        )

        message = OutreachMessage(
            candidate_username="testuser",
            rank=1,
            message_text="Hi testuser, I noticed your awesome-project...",
            tone=ToneStyle.FORMAL,
            confidence_score=92.5,
            personalization_metadata=metadata,
            tokens_used=250
        )

        assert message.candidate_username == "testuser"
        assert message.rank == 1
        assert message.message_text.startswith("Hi testuser")
        assert message.tone == ToneStyle.FORMAL
        assert message.confidence_score == 92.5
        assert message.personalization_metadata == metadata
        assert message.tokens_used == 250
        assert message.fallback_applied is False
        assert isinstance(message.generated_at, datetime)

    def test_default_tone_is_formal(self):
        """Test default tone is FORMAL."""
        metadata = PersonalizationMetadata()
        message = OutreachMessage(
            candidate_username="user",
            rank=5,
            message_text="Test message",
            confidence_score=80.0,
            personalization_metadata=metadata
        )

        assert message.tone == ToneStyle.FORMAL

    def test_confidence_score_validation_too_low(self):
        """Test confidence_score must be >= 0."""
        metadata = PersonalizationMetadata()

        with pytest.raises(ValidationError) as exc_info:
            OutreachMessage(
                candidate_username="user",
                rank=1,
                message_text="Test",
                confidence_score=-1.0,
                personalization_metadata=metadata
            )

        assert "greater_than_equal" in str(exc_info.value)

    def test_confidence_score_validation_too_high(self):
        """Test confidence_score must be <= 100."""
        metadata = PersonalizationMetadata()

        with pytest.raises(ValidationError) as exc_info:
            OutreachMessage(
                candidate_username="user",
                rank=1,
                message_text="Test",
                confidence_score=101.0,
                personalization_metadata=metadata
            )

        assert "less_than_equal" in str(exc_info.value)

    def test_rank_validation_must_be_positive(self):
        """Test rank must be >= 1."""
        metadata = PersonalizationMetadata()

        with pytest.raises(ValidationError) as exc_info:
            OutreachMessage(
                candidate_username="user",
                rank=0,
                message_text="Test",
                confidence_score=80.0,
                personalization_metadata=metadata
            )

        assert "greater_than_equal" in str(exc_info.value)

    def test_tone_validation_must_be_valid_enum(self):
        """Test tone must be valid ToneStyle enum."""
        metadata = PersonalizationMetadata()

        # Valid enum values work
        for tone in [ToneStyle.FORMAL, ToneStyle.CASUAL]:
            message = OutreachMessage(
                candidate_username="user",
                rank=1,
                message_text="Test",
                tone=tone,
                confidence_score=80.0,
                personalization_metadata=metadata
            )
            assert message.tone == tone

    def test_profile_url_computed_property(self):
        """Test profile_url computed property."""
        metadata = PersonalizationMetadata()
        message = OutreachMessage(
            candidate_username="johndoe",
            rank=3,
            message_text="Test message",
            confidence_score=75.0,
            personalization_metadata=metadata
        )

        assert message.profile_url == "https://github.com/johndoe"

    def test_fallback_applied_flag(self):
        """Test fallback_applied flag works correctly."""
        metadata = PersonalizationMetadata()

        # Default is False
        message1 = OutreachMessage(
            candidate_username="user",
            rank=1,
            message_text="Test",
            confidence_score=80.0,
            personalization_metadata=metadata
        )
        assert message1.fallback_applied is False

        # Can set to True
        message2 = OutreachMessage(
            candidate_username="user",
            rank=1,
            message_text="Test",
            confidence_score=50.0,
            personalization_metadata=metadata,
            fallback_applied=True
        )
        assert message2.fallback_applied is True

    def test_tokens_used_defaults_to_zero(self):
        """Test tokens_used defaults to 0."""
        metadata = PersonalizationMetadata()
        message = OutreachMessage(
            candidate_username="user",
            rank=1,
            message_text="Test",
            confidence_score=80.0,
            personalization_metadata=metadata
        )

        assert message.tokens_used == 0

    def test_empty_message_text_allowed(self):
        """Test empty message_text is allowed (edge case)."""
        metadata = PersonalizationMetadata()
        message = OutreachMessage(
            candidate_username="user",
            rank=1,
            message_text="",
            confidence_score=20.0,
            personalization_metadata=metadata,
            fallback_applied=True
        )

        assert message.message_text == ""


class TestToneStyle:
    """Test ToneStyle enum."""

    def test_tone_style_values(self):
        """Test ToneStyle enum has correct values."""
        assert ToneStyle.FORMAL.value == "formal"
        assert ToneStyle.CASUAL.value == "casual"

    def test_tone_style_string_comparison(self):
        """Test ToneStyle can be compared with strings."""
        assert ToneStyle.FORMAL == "formal"
        assert ToneStyle.CASUAL == "casual"
