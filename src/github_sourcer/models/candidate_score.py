"""
CandidateScore Model
====================
Represents scored candidate with ensemble scoring breakdown.

Part of Module 002: GitHub Sourcer - Enhanced Ensemble Scoring
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict


class CandidateScore(BaseModel):
    """
    Scored candidate with ensemble scoring breakdown.

    Supports:
    - Total weighted score (0.0-1.0)
    - Individual signal scores (skill, location, activity)
    - Signal contribution breakdown for transparency
    """

    username: str = Field(
        ...,
        description="GitHub username"
    )

    total_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Total weighted ensemble score (0.0-1.0)"
    )

    skill_match_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Skill matching score (0.0-1.0)"
    )

    location_match_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Location matching score (0.0-1.0)"
    )

    activity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Activity score based on repos/followers/recency (0.0-1.0)"
    )

    signal_contributions: Dict[str, float] = Field(
        default_factory=dict,
        description="Breakdown of each signal's contribution to total_score"
    )

    @field_validator('total_score', 'skill_match_score', 'location_match_score', 'activity_score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Ensure scores are between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {v}")
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username is not empty"""
        if not v or not v.strip():
            raise ValueError("username must not be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "total_score": 0.85,
                "skill_match_score": 0.9,
                "location_match_score": 0.8,
                "activity_score": 0.7,
                "signal_contributions": {
                    "skill_match": 0.45,
                    "location_match": 0.24,
                    "activity": 0.14
                }
            }
        }
