"""
Outreach Generator Data Models

This module defines Pydantic models for the outreach generation system.
Supports 3-stage pipeline (Analysis → Generation → Refinement) with
multi-channel optimization (Email, LinkedIn, Twitter).
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ChannelType(str, Enum):
    """Communication channels for outreach messages."""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class FollowUpAngle(str, Enum):
    """Follow-up message angles for different sequences."""
    REMINDER = "reminder"  # Day 3: Brief reminder with different repo
    TECHNICAL_CHALLENGE = "technical_challenge"  # Day 7: Technical problem preview
    CAREER_GROWTH = "career_growth"  # Alternative: Career progression emphasis
    SOFT_CLOSE = "soft_close"  # Day 14: Final gentle close with opt-out


class PersonalizationMetadata(BaseModel):
    """
    Metadata tracking how personalization was applied to a message.

    Captures the elements used for personalization and quality indicators.
    """
    referenced_repositories: list[str] = Field(
        default_factory=list,
        description="List of GitHub repository names mentioned in the message"
    )
    technical_details_mentioned: list[str] = Field(
        default_factory=list,
        description="Specific code features or technical implementations referenced"
    )
    enrichment_data_used: dict = Field(
        default_factory=dict,
        description="Which enrichment fields were used (email, linkedin, twitter, blog, company)"
    )
    analysis_insights: dict = Field(
        default_factory=dict,
        description="Stage 1 LLM analysis output (achievements, passion_areas, trajectory, starters)"
    )
    cliches_removed: list[str] = Field(
        default_factory=list,
        description="List of recruiter clichés detected and removed in Stage 3"
    )
    quality_flags: list[str] = Field(
        default_factory=list,
        description="Quality issues flagged (e.g., 'low_personalization')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "referenced_repositories": ["redis-clone", "async-patterns"],
                "technical_details_mentioned": ["concurrent writes with locks", "async/await patterns"],
                "enrichment_data_used": {"email": True, "linkedin": True, "company": "TechCorp"},
                "analysis_insights": {
                    "achievements": ["Built distributed caching system", "Open source contributor"],
                    "passion_areas": ["Systems programming", "Performance optimization"]
                },
                "cliches_removed": ["reaching out", "great opportunity"],
                "quality_flags": []
            }
        }


class OutreachMessage(BaseModel):
    """
    Generated personalized outreach message for a candidate.

    Represents the output of the 3-stage pipeline (Analysis → Generation → Refinement)
    optimized for a specific communication channel.
    """
    shortlist_id: str = Field(
        description="Foreign key to shortlisted candidate"
    )
    channel: ChannelType = Field(
        description="Communication channel (email, linkedin, twitter)"
    )
    subject_line: Optional[str] = Field(
        default=None,
        description="Email subject line (36-50 chars, email only)"
    )
    message_text: str = Field(
        description="Main message body (channel-specific length constraints)"
    )
    personalization_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Quality score 0-100 based on personalization depth"
    )
    personalization_metadata: PersonalizationMetadata = Field(
        description="Detailed personalization tracking"
    )
    tokens_used: int = Field(
        ge=0,
        description="Total LLM tokens consumed across all 3 stages"
    )
    stage_breakdown: dict = Field(
        default_factory=dict,
        description="Tokens per stage: {analysis: X, generation: Y, refinement: Z}"
    )
    is_edited: bool = Field(
        default=False,
        description="Whether user has manually edited this message"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when message was generated"
    )
    edited_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when message was last edited"
    )

    @field_validator("subject_line")
    @classmethod
    def validate_subject_line(cls, v: Optional[str], info) -> Optional[str]:
        """Validate email subject line is 36-50 chars if present."""
        if v is not None:
            if len(v) < 36 or len(v) > 50:
                raise ValueError("Email subject line must be 36-50 characters")
        return v

    @field_validator("channel")
    @classmethod
    def validate_email_has_subject(cls, v: ChannelType, info) -> ChannelType:
        """Ensure email messages have subject lines."""
        # Note: This validation runs before subject_line, so we can't check it here
        # Will be validated in business logic
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "shortlist_id": "12345",
                "channel": "email",
                "subject_line": "Your redis-clone project + Backend @ TechCorp",
                "message_text": "Hi Sarah,\n\nCame across your redis-clone implementation...",
                "personalization_score": 85.0,
                "personalization_metadata": {
                    "referenced_repositories": ["redis-clone"],
                    "technical_details_mentioned": ["concurrent writes with locks"]
                },
                "tokens_used": 1500,
                "stage_breakdown": {"analysis": 500, "generation": 700, "refinement": 300},
                "is_edited": False,
                "generated_at": "2025-10-10T12:00:00Z"
            }
        }


class FollowUpSequence(BaseModel):
    """
    Follow-up message in a multi-touch outreach sequence.

    Part of a 3-message follow-up sequence with different angles
    scheduled at specific intervals (Day 3, 7, 14).
    """
    outreach_message_id: str = Field(
        description="Foreign key to original outreach message"
    )
    sequence_number: int = Field(
        ge=1,
        le=3,
        description="Sequence position (1, 2, or 3)"
    )
    scheduled_days_after: int = Field(
        description="Days after original message to send (3, 7, or 14)"
    )
    message_text: str = Field(
        description="Follow-up message content"
    )
    angle: FollowUpAngle = Field(
        description="Message angle (reminder, technical_challenge, career_growth, soft_close)"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when follow-up was generated"
    )

    @field_validator("scheduled_days_after")
    @classmethod
    def validate_scheduled_days(cls, v: int) -> int:
        """Validate scheduled_days_after is 3, 7, or 14."""
        if v not in [3, 7, 14]:
            raise ValueError("scheduled_days_after must be 3, 7, or 14")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "outreach_message_id": "67890",
                "sequence_number": 1,
                "scheduled_days_after": 3,
                "message_text": "Quick follow-up on my previous message...",
                "angle": "reminder",
                "generated_at": "2025-10-10T12:00:00Z"
            }
        }
