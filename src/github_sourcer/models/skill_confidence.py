"""
SkillConfidence Model
=====================
Represents detected skill with confidence score and detection signals.

Part of Module 002: GitHub Sourcer - Enhanced Skill Detection
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict


class SkillConfidence(BaseModel):
    """
    Skill detection result with confidence scoring.

    Supports:
    - Primary detection via dependency graphs (80-85% accuracy)
    - Ensemble detection via topics/bio/languages (70-75% accuracy)
    - Multi-signal aggregation with weighted scoring
    """

    skill_name: str = Field(
        ...,
        description="Normalized skill name (e.g., 'React', 'Python')"
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )

    detection_signals: list[str] = Field(
        ...,
        description="List of signals that detected this skill (e.g., ['dependency_graph', 'repository_topics'])"
    )

    signal_weights: Dict[str, float] = Field(
        default_factory=dict,
        description="Weight of each detection signal used in scoring"
    )

    is_primary_detection: bool = Field(
        default=False,
        description="True if detected via primary method (dependency graph), False if via ensemble"
    )

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confidence_score must be between 0.0 and 1.0, got {v}")
        return v

    @field_validator('detection_signals')
    @classmethod
    def validate_detection_signals(cls, v: list[str]) -> list[str]:
        """Ensure detection_signals is not empty"""
        if not v or len(v) == 0:
            raise ValueError("detection_signals must not be empty")
        return v

    @field_validator('skill_name')
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        """Ensure skill_name is not empty"""
        if not v or not v.strip():
            raise ValueError("skill_name must not be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "skill_name": "Pandas",
                "confidence_score": 0.85,
                "detection_signals": ["dependency_graph", "repository_language"],
                "signal_weights": {
                    "dependency_graph": 0.8,
                    "repository_language": 0.3
                },
                "is_primary_detection": True
            }
        }
