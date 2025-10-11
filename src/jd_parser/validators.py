"""Input/output validators for JD Parser."""

from pydantic import ValidationError
from .models import FreeTextInput, JobRequirement


def validate_input(text: str, language: str = "en") -> FreeTextInput:
    """
    Validate input text conforms to FreeTextInput schema.

    Args:
        text: Free-text job description
        language: Input language (default: "en")

    Returns:
        Validated FreeTextInput object

    Raises:
        ValidationError: If input is invalid
    """
    return FreeTextInput(text=text, language=language)


def validate_output(job_req: JobRequirement) -> JobRequirement:
    """
    Validate output conforms to JobRequirement schema.

    Args:
        job_req: JobRequirement object to validate

    Returns:
        Validated JobRequirement object

    Raises:
        ValidationError: If output is invalid (e.g., missing minimum fields)
    """
    # Pydantic validation happens automatically on construction
    # This explicitly re-validates to catch any post-construction issues
    return JobRequirement.model_validate(job_req.model_dump())


def validate_minimum_fields(job_req: JobRequirement) -> bool:
    """
    Check if JobRequirement meets minimum field requirements (FR-011).

    Args:
        job_req: JobRequirement to check

    Returns:
        True if valid, False otherwise

    Note:
        This is already enforced by JobRequirement.validate_minimum_fields()
        but provided as a standalone function for explicit checks.
    """
    return job_req.role is not None or len(job_req.required_skills) > 0
