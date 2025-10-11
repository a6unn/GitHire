"""Pydantic models for Ranking Engine module."""

from typing import Optional
from pydantic import BaseModel, Field, model_validator

from src.github_sourcer.models.candidate import Candidate


class ScoreBreakdown(BaseModel):
    """Explanation of how scores were calculated."""

    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills from job requirement found in candidate profile"
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Skills from job requirement not found in candidate profile"
    )
    activity_reasoning: str = Field(
        ...,
        min_length=1,
        description="Explanation of activity score"
    )
    experience_reasoning: str = Field(
        ...,
        min_length=1,
        description="Explanation of experience score"
    )
    domain_reasoning: str = Field(
        ...,
        min_length=1,
        description="Explanation of domain relevance score"
    )


class ScoreWeights(BaseModel):
    """Configurable weights for score combination."""

    skill_match_weight: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Weight for skill match score (default 40%)"
    )
    experience_weight: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for experience score (default 20%)"
    )
    activity_weight: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for activity score (default 20%)"
    )
    domain_weight: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight for domain relevance score (default 20%)"
    )

    @model_validator(mode='after')
    def weights_sum_to_one(self):
        """Ensure weights sum to 1.0 (with small tolerance for floating point)."""
        total = (
            self.skill_match_weight +
            self.experience_weight +
            self.activity_weight +
            self.domain_weight
        )
        if not 0.99 <= total <= 1.01:
            raise ValueError(
                f"Weights must sum to 1.0 (got {total:.4f}). "
                f"Weights: skill={self.skill_match_weight}, "
                f"experience={self.experience_weight}, "
                f"activity={self.activity_weight}, "
                f"domain={self.domain_weight}"
            )
        return self


class RankedCandidate(BaseModel):
    """A candidate with ranking scores and position."""

    # Original candidate data
    candidate: Candidate = Field(
        ...,
        description="Original candidate from GitHub Sourcer"
    )

    # Ranking metadata
    rank: int = Field(
        ...,
        ge=1,
        description="Position in ranked list (1 = best match)"
    )
    total_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Weighted combination of all scores (0-100)"
    )

    # Individual scores
    skill_match_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of required skills matched (0-100)"
    )
    activity_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Activity level score based on contributions (0-100)"
    )
    experience_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Experience score based on account age and repos (0-100)"
    )
    domain_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Domain relevance score (0-100)"
    )

    # Transparency
    score_breakdown: ScoreBreakdown = Field(
        ...,
        description="Detailed explanation of scores"
    )

    # Convenience properties for easier access
    @property
    def github_username(self) -> str:
        """Return candidate's GitHub username."""
        return self.candidate.github_username

    @property
    def name(self) -> Optional[str]:
        """Return candidate's name."""
        return self.candidate.name

    @property
    def profile_url(self) -> str:
        """Return candidate's GitHub profile URL."""
        return self.candidate.profile_url

    def flatten_for_api(self) -> dict:
        """Flatten nested candidate structure for API responses.

        This flattens the nested `candidate` object so frontend can access
        fields like `github_username` directly instead of `candidate.github_username`.

        Returns:
            Dictionary with candidate fields at top level + ranking fields
        """
        # Get all candidate fields as dict
        candidate_dict = self.candidate.model_dump(mode='json')

        # Build score_breakdown with both skill lists AND individual score percentages
        score_breakdown_dict = self.score_breakdown.model_dump(mode='json')
        score_breakdown_dict['skill_match'] = self.skill_match_score
        score_breakdown_dict['experience'] = self.experience_score
        score_breakdown_dict['activity'] = self.activity_score

        # Extract strengths from reasoning fields for UI display
        strengths = []

        # Skill match strengths
        if self.skill_match_score >= 80:
            strengths.append(f"Excellent skill match ({len(self.score_breakdown.matched_skills)} skills)")
        elif self.skill_match_score >= 50:
            strengths.append(f"Good skill match ({len(self.score_breakdown.matched_skills)} skills)")

        # Activity strengths
        if self.activity_score >= 70:
            strengths.append("High GitHub activity")
        elif self.activity_score >= 40:
            strengths.append("Active contributor")

        # Experience strengths
        if self.experience_score >= 70:
            strengths.append("Experienced developer")
        elif self.experience_score >= 40:
            strengths.append("Established profile")

        # Get ranking fields
        ranking_dict = {
            'rank': self.rank,
            'total_score': self.total_score,
            'domain_score': self.domain_score,
            'score_breakdown': score_breakdown_dict,
            'strengths': strengths,
            'concerns': [],  # Placeholder for future enhancement
        }

        # Merge candidate fields with ranking fields (ranking fields take precedence)
        return {**candidate_dict, **ranking_dict}
