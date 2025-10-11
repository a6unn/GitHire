"""SQLAlchemy database models for Backend API."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON, Enum as SQLEnum, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class ProjectStatus(str, enum.Enum):
    """Project workflow status."""
    DRAFT = "draft"
    SOURCING = "sourcing"
    SOURCED = "sourced"
    RANKING = "ranking"
    RANKED = "ranked"
    SHORTLISTED = "shortlisted"
    # Legacy statuses for backward compatibility
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EnrichmentStatus(str, enum.Enum):
    """Enrichment status for shortlisted candidates."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OutreachStatus(str, enum.Enum):
    """Outreach message status."""
    DRAFT = "draft"
    SENT = "sent"


class ChannelType(str, enum.Enum):
    """Outreach channel type (Module 004)."""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class FollowUpAngle(str, enum.Enum):
    """Follow-up sequence angle (Module 004)."""
    REMINDER = "reminder"
    TECHNICAL_CHALLENGE = "technical_challenge"
    CAREER_GROWTH = "career_growth"
    SOFT_CLOSE = "soft_close"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # User's display name
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.user_id:
            self.user_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email})>"


class Project(Base):
    """Saved recruitment pipeline run."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Project name
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Job role title
    job_description_text: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Job location
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    pipeline_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    pipeline_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_score: Mapped[Optional[float]] = mapped_column(nullable=True)  # Average candidate score
    results_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    shortlisted_candidates: Mapped[list["ShortlistedCandidate"]] = relationship("ShortlistedCandidate", back_populates="project", cascade="all, delete-orphan")
    outreach_messages: Mapped[list["OutreachMessage"]] = relationship("OutreachMessage", back_populates="project", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.project_id:
            self.project_id = str(uuid.uuid4())
        if not self.status:
            self.status = ProjectStatus.DRAFT
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
        if self.candidate_count is None:
            self.candidate_count = 0

    def __repr__(self) -> str:
        return f"<Project(project_id={self.project_id}, status={self.status.value})>"


class ShortlistedCandidate(Base):
    """Candidate manually selected by user for further action."""

    __tablename__ = "shortlisted_candidates"
    __table_args__ = (
        UniqueConstraint('project_id', 'github_username', name='uix_project_candidate'),
    )

    shortlist_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)
    github_username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    candidate_data: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full RankedCandidate data
    enriched_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional GitHub data
    enrichment_status: Mapped[EnrichmentStatus] = mapped_column(SQLEnum(EnrichmentStatus), default=EnrichmentStatus.PENDING, nullable=False)
    enriched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="shortlisted_candidates")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.shortlist_id:
            self.shortlist_id = str(uuid.uuid4())
        if not self.enrichment_status:
            self.enrichment_status = EnrichmentStatus.PENDING
        if not self.created_at:
            self.created_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<ShortlistedCandidate(shortlist_id={self.shortlist_id}, project_id={self.project_id}, github_username={self.github_username})>"


class OutreachMessage(Base):
    """Personalized outreach message generated for a shortlisted candidate (Module 004).

    Supports multi-channel outreach (email, LinkedIn, Twitter) with personalization scoring,
    cliché detection, and 3-stage LLM pipeline tracking.
    """

    __tablename__ = "outreach_messages"
    __table_args__ = (
        # One message per channel per candidate per project
        UniqueConstraint('project_id', 'github_username', 'channel', name='uix_project_outreach_channel'),
    )

    outreach_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.project_id"), nullable=False, index=True)
    github_username: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Module 004: Multi-channel support
    channel: Mapped[ChannelType] = mapped_column(SQLEnum(ChannelType), nullable=False)
    subject_line: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Email only, 36-50 chars
    message_text: Mapped[str] = mapped_column(Text, nullable=False)  # Generated message body

    # Module 004: Personalization metrics
    personalization_score: Mapped[float] = mapped_column(nullable=False)  # 0-100
    personalization_metadata: Mapped[dict] = mapped_column(JSON, nullable=False)  # Detailed breakdown

    # Module 004: Token tracking
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)  # Total tokens
    stage_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)  # Per-stage tokens

    # Editing tracking
    is_edited: Mapped[bool] = mapped_column(nullable=False, default=False)
    edited_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # User-edited version
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Status tracking
    status: Mapped[OutreachStatus] = mapped_column(SQLEnum(OutreachStatus), default=OutreachStatus.DRAFT, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="outreach_messages")
    follow_ups: Mapped[list["FollowUpSequence"]] = relationship("FollowUpSequence", back_populates="outreach_message", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.outreach_id:
            self.outreach_id = str(uuid.uuid4())
        if not self.status:
            self.status = OutreachStatus.DRAFT
        if self.is_edited is None:
            self.is_edited = False
        if not self.generated_at:
            self.generated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<OutreachMessage(outreach_id={self.outreach_id}, channel={self.channel.value}, github_username={self.github_username}, score={self.personalization_score})>"


class FollowUpSequence(Base):
    """Follow-up message sequence for outreach (Module 004).

    Supports 3-part follow-up sequences with different angles:
    - Day 3 (Reminder): Brief reminder with different repo mention
    - Day 7 (Technical Challenge): Technical problem preview
    - Day 14 (Soft Close): Gentle opt-out option
    """

    __tablename__ = "follow_up_sequences"

    followup_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    outreach_message_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_messages.outreach_id"), nullable=False, index=True)

    # Sequence details
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3
    scheduled_days_after: Mapped[int] = mapped_column(Integer, nullable=False)  # 3, 7, or 14
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[FollowUpAngle] = mapped_column(SQLEnum(FollowUpAngle), nullable=False)

    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    outreach_message: Mapped["OutreachMessage"] = relationship("OutreachMessage", back_populates="follow_ups")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.followup_id:
            self.followup_id = str(uuid.uuid4())
        if not self.generated_at:
            self.generated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<FollowUpSequence(followup_id={self.followup_id}, sequence={self.sequence_number}, angle={self.angle.value})>"


class Session(Base):
    """User authentication session."""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=24),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)

    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, user_id={self.user_id})>"

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at


class PasswordResetToken(Base):
    """Password reset token for user account recovery."""

    __tablename__ = "password_reset_tokens"

    token_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=1),  # Token expires in 1 hour
        nullable=False
    )
    used: Mapped[bool] = mapped_column(default=False, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token_id:
            self.token_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
        if self.used is None:
            self.used = False

    def __repr__(self) -> str:
        return f"<PasswordResetToken(token_id={self.token_id}, user_id={self.user_id}, used={self.used})>"

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not used and not expired)."""
        return not self.used and not self.is_expired
