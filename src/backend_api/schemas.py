"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User information response."""

    user_id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Request to update user profile."""

    name: str = Field(..., min_length=1, max_length=255, description="User's display name")


class ChangePasswordRequest(BaseModel):
    """Request to change password for authenticated user."""

    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password reset."""

    email: EmailStr = Field(..., description="Email address of account to reset")


class ForgotPasswordResponse(BaseModel):
    """Response after requesting password reset."""

    message: str = Field(..., description="Success message")
    reset_token: Optional[str] = Field(None, description="Reset token (for testing only, not in production)")


class ResetPasswordRequest(BaseModel):
    """Request to reset password with token."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")


# Pipeline Schemas

class PipelineRunRequest(BaseModel):
    """Request to run recruitment pipeline."""

    job_description_text: str = Field(
        ..., min_length=10, max_length=10000, description="Job description text"
    )


class PipelineRunResponse(BaseModel):
    """Response from pipeline execution."""

    project_id: str = Field(..., description="Project ID for tracking")
    status: str = Field(..., description="Pipeline status (success/failed)")
    candidates: list[dict[str, Any]] = Field(default_factory=list, description="List of candidates found")
    ranked_candidates: list[dict[str, Any]] = Field(default_factory=list, description="Ranked candidates")
    outreach_messages: list[dict[str, Any]] = Field(default_factory=list, description="Generated outreach messages")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution metadata")


class PipelineStatusResponse(BaseModel):
    """Pipeline execution status."""

    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="Current status (running/completed/failed)")
    current_module: Optional[str] = Field(None, description="Currently executing module")
    progress_percentage: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    started_at: Optional[datetime] = Field(None, description="Pipeline start time")
    completed_at: Optional[datetime] = Field(None, description="Pipeline completion time")


# Project Schemas

class ProjectSummary(BaseModel):
    """Project summary for list view."""

    project_id: str = Field(..., description="Project ID")
    name: Optional[str] = Field(None, description="Project name")
    job_title: Optional[str] = Field(None, description="Job role title")
    status: str = Field(..., description="Project status (draft/sourcing/sourced/ranking/ranked/shortlisted)")
    job_description_text: str = Field(..., description="Job description text (first 200 chars)")
    candidate_count: int = Field(..., description="Number of candidates found")
    avg_score: Optional[float] = Field(None, description="Average candidate score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    pipeline_start_time: Optional[datetime] = Field(None, description="Pipeline start time")
    pipeline_end_time: Optional[datetime] = Field(None, description="Pipeline end time")

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response containing list of projects."""

    projects: list[ProjectSummary] = Field(default_factory=list, description="List of projects")
    total: int = Field(..., description="Total number of projects")


class ProjectDetailResponse(BaseModel):
    """Detailed project information with full results."""

    project_id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="Owner user ID")
    name: Optional[str] = Field(None, description="Project name")
    job_title: Optional[str] = Field(None, description="Job role title")
    status: str = Field(..., description="Project status (draft/sourcing/sourced/ranking/ranked/shortlisted)")
    job_description_text: str = Field(..., description="Full job description")
    candidate_count: int = Field(..., description="Number of candidates")
    avg_score: Optional[float] = Field(None, description="Average candidate score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")
    pipeline_start_time: Optional[datetime] = Field(None, description="Pipeline start time")
    pipeline_end_time: Optional[datetime] = Field(None, description="Pipeline end time")
    results_json: Optional[dict[str, Any]] = Field(None, description="Full pipeline results")

    class Config:
        from_attributes = True


# Multi-Stage Workflow Schemas

class QuickStartParseRequest(BaseModel):
    """Request to parse quick-start text into project fields."""

    quick_text: str = Field(..., min_length=10, max_length=1000, description="Natural language description of the job search")


class QuickStartParseResponse(BaseModel):
    """Response from parsing quick-start text."""

    project_name: str = Field(..., description="Suggested project name")
    job_title: str = Field(..., description="Extracted job title")
    location: Optional[str] = Field(None, description="Extracted location")
    skills: list[str] = Field(default_factory=list, description="Extracted skills")
    experience_years: Optional[str] = Field(None, description="Extracted years of experience")
    job_description_text: str = Field(..., description="Generated job description from quick text")


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    job_title: str = Field(..., min_length=1, max_length=255, description="Job role title (e.g., 'Senior Python Developer')")
    job_description_text: str = Field(..., min_length=10, max_length=10000, description="Full job description")
    location: Optional[str] = Field(None, max_length=500, description="Job location (e.g., 'Chennai, Tamil Nadu, India')")


class SourceCandidatesResponse(BaseModel):
    """Response from sourcing candidates."""

    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="New project status (sourced)")
    candidates: list[dict[str, Any]] = Field(default_factory=list, description="List of sourced candidates")
    candidate_count: int = Field(..., description="Number of candidates found")


class RankCandidatesResponse(BaseModel):
    """Response from ranking candidates."""

    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="New project status (ranked)")
    ranked_candidates: list[dict[str, Any]] = Field(default_factory=list, description="List of ranked candidates")
    avg_score: float = Field(..., description="Average score of all candidates")


class ShortlistCandidatesRequest(BaseModel):
    """Request to shortlist selected candidates."""

    candidate_usernames: list[str] = Field(..., min_length=1, description="List of GitHub usernames to shortlist")


class ShortlistCandidatesResponse(BaseModel):
    """Response after shortlisting candidates."""

    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="New project status (shortlisted)")
    shortlisted_count: int = Field(..., description="Number of candidates shortlisted")


class ShortlistedCandidateResponse(BaseModel):
    """Shortlisted candidate with enrichment info."""

    shortlist_id: str = Field(..., description="Shortlist entry ID")
    project_id: str = Field(..., description="Project ID")
    github_username: str = Field(..., description="GitHub username")
    candidate_data: dict[str, Any] = Field(..., description="Full RankedCandidate data")
    enriched_data: Optional[dict[str, Any]] = Field(None, description="Additional enriched data")
    enrichment_status: str = Field(..., description="Enrichment status (pending/in_progress/completed/failed)")
    enriched_at: Optional[datetime] = Field(None, description="When enrichment completed")
    created_at: datetime = Field(..., description="When shortlisted")

    class Config:
        from_attributes = True


class ToggleShortlistResponse(BaseModel):
    """Response after toggling shortlist status for a candidate."""

    project_id: str = Field(..., description="Project ID")
    github_username: str = Field(..., description="GitHub username")
    is_shortlisted: bool = Field(..., description="True if now shortlisted, False if removed")
    shortlisted_count: int = Field(..., description="Total shortlisted count for project")


class EnrichCandidateResponse(BaseModel):
    """Response from enriching a candidate."""

    shortlist_id: str = Field(..., description="Shortlist entry ID")
    github_username: str = Field(..., description="GitHub username")
    enrichment_status: str = Field(..., description="Enrichment status")
    enriched_data: dict[str, Any] = Field(..., description="Enriched profile data")
    enriched_at: datetime = Field(..., description="Enrichment completion time")


# ============================================================================
# Module 004: Outreach Generator Schemas
# ============================================================================

class GenerateOutreachRequest(BaseModel):
    """Request to generate outreach message (Module 004)."""
    # No body needed - uses path params and candidate data from shortlist


class OutreachMessageResponse(BaseModel):
    """Outreach message response (Module 004 - Multi-channel support)."""

    outreach_id: str = Field(..., description="Outreach message ID")
    project_id: str = Field(..., description="Project ID")
    github_username: str = Field(..., description="GitHub username")

    # Module 004: Multi-channel support
    channel: str = Field(..., description="Channel type (email/linkedin/twitter)")
    subject_line: Optional[str] = Field(None, description="Email subject line (36-50 chars, email only)")
    message_text: str = Field(..., description="Generated message body")

    # Module 004: Personalization metrics
    personalization_score: float = Field(..., ge=0.0, le=100.0, description="Personalization score (0-100)")
    personalization_metadata: dict[str, Any] = Field(..., description="Detailed personalization breakdown")

    # Module 004: Token tracking
    tokens_used: int = Field(..., ge=0, description="Total tokens used")
    stage_breakdown: dict[str, Any] = Field(..., description="Per-stage token breakdown")

    # Editing tracking
    is_edited: bool = Field(..., description="Whether message has been edited")
    edited_message: Optional[str] = Field(None, description="User-edited version")
    edited_at: Optional[datetime] = Field(None, description="When edited")

    # Status tracking
    status: str = Field(..., description="Message status (draft/sent)")
    sent_at: Optional[datetime] = Field(None, description="When marked as sent")
    generated_at: datetime = Field(..., description="When generated")

    class Config:
        from_attributes = True


class UpdateOutreachRequest(BaseModel):
    """Request to update (edit) outreach message (Module 004)."""

    message_text: str = Field(..., min_length=1, description="Edited message text")


class MarkOutreachSentRequest(BaseModel):
    """Request to mark outreach as sent (Module 004)."""
    # No body needed - just updates status and timestamp


class FollowUpSequenceResponse(BaseModel):
    """Follow-up sequence response (Module 004)."""

    followup_id: str = Field(..., description="Follow-up ID")
    outreach_message_id: str = Field(..., description="Parent outreach message ID")
    sequence_number: int = Field(..., ge=1, le=3, description="Sequence number (1-3)")
    scheduled_days_after: int = Field(..., description="Days after original (3, 7, or 14)")
    message_text: str = Field(..., description="Follow-up message text")
    angle: str = Field(..., description="Follow-up angle (reminder/technical_challenge/career_growth/soft_close)")
    generated_at: datetime = Field(..., description="When generated")
    sent_at: Optional[datetime] = Field(None, description="When sent")

    class Config:
        from_attributes = True


class GenerateFollowUpsResponse(BaseModel):
    """Response from generating follow-up sequences (Module 004)."""

    outreach_message_id: str = Field(..., description="Outreach message ID")
    follow_ups: list[FollowUpSequenceResponse] = Field(..., description="Generated follow-ups (3 total)")


class GenerateOutreachResponse(BaseModel):
    """Response from generating outreach messages (Module 004)."""

    project_id: str = Field(..., description="Project ID")
    github_username: str = Field(..., description="GitHub username")
    messages: list[OutreachMessageResponse] = Field(..., description="Generated messages (1-3 channels)")


class RegenerateOutreachResponse(BaseModel):
    """Response from regenerating an outreach message (Module 004)."""

    project_id: str = Field(..., description="Project ID")
    github_username: str = Field(..., description="GitHub username")
    channel: str = Field(..., description="Channel type")
    message: OutreachMessageResponse = Field(..., description="Regenerated message")
