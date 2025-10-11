"""
Outreach Generator Module (Module 004)

Generates personalized, research-backed outreach messages for shortlisted GitHub candidates
using 3-stage LLM pipeline (Analysis → Generation → Refinement) with multi-channel optimization.

Target: 30-50% response rate (vs industry average 5-12%)
"""

from .models import (
    ChannelType,
    FollowUpAngle,
    PersonalizationMetadata,
    OutreachMessage,
    FollowUpSequence,
)

__version__ = "0.1.0"

__all__ = [
    "ChannelType",
    "FollowUpAngle",
    "PersonalizationMetadata",
    "OutreachMessage",
    "FollowUpSequence",
]
