"""
LocationHierarchy Model
=======================
Represents parsed location with hierarchical components (city/state/country).

Part of Module 002: GitHub Sourcer - Enhanced Location Matching
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class LocationHierarchy(BaseModel):
    """
    Hierarchical location representation for matching.

    Supports city/state/country hierarchy with confidence scoring.
    """

    original_text: str = Field(
        ...,
        description="Original location string from user profile"
    )

    city: Optional[str] = Field(
        None,
        description="Parsed city name (canonical form)"
    )

    state: Optional[str] = Field(
        None,
        description="Parsed state/province name"
    )

    country: Optional[str] = Field(
        None,
        description="Parsed country name"
    )

    match_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the parsing/matching (0.0-1.0)"
    )

    match_level: Optional[str] = Field(
        None,
        description="Level of match: 'city', 'state', 'country', or None"
    )

    @field_validator('match_confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"match_confidence must be between 0.0 and 1.0, got {v}")
        return v

    @field_validator('match_level')
    @classmethod
    def validate_match_level(cls, v: Optional[str]) -> Optional[str]:
        """Ensure match_level is valid"""
        if v is not None and v not in ["city", "state", "country"]:
            raise ValueError(f"match_level must be 'city', 'state', 'country', or None, got {v}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "Chennai, Tamil Nadu, India",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "country": "India",
                "match_confidence": 1.0,
                "match_level": "city"
            }
        }
