"""JD Parser Module - Extracts structured job requirements from free-text job descriptions."""

from .parser import JDParser
from .models import JobRequirement, YearsOfExperience, ConfidenceScore

__version__ = "0.1.0"


def parse_jd(jd_text: str, language: str = "en") -> JobRequirement:
    """
    Parse job description and extract structured requirements.

    Args:
        jd_text: Free-text job description
        language: Input language (default: "en")

    Returns:
        JobRequirement object with extracted data
    """
    parser = JDParser()
    return parser.parse(jd_text, language)


__all__ = ["parse_jd", "JDParser", "JobRequirement", "YearsOfExperience", "ConfidenceScore"]
