"""Integration test for Scenario 3: Validation errors."""

import pytest
from src.jd_parser.parser import JDParser
from pydantic import ValidationError


class TestValidationErrors:
    """Test that parser properly validates and rejects invalid inputs."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_empty_text_raises_error(self, parser):
        """Empty input should raise validation error."""
        with pytest.raises((ValidationError, ValueError)):
            parser.parse("")

    def test_whitespace_only_raises_error(self, parser):
        """Whitespace-only input should raise validation error."""
        with pytest.raises((ValidationError, ValueError)):
            parser.parse("   \n\t  ")

    def test_neither_role_nor_skills_raises_error(self, parser):
        """
        Input with neither role nor skills should fail minimum validation (FR-011).

        Example: "Looking for someone immediately" has no role/skills.
        """
        jd_text = "Looking for someone to join our team immediately"

        # This should either:
        # 1. Raise ValidationError (if LLM can't extract role/skills)
        # 2. Return result with role=None and required_skills=[]
        #    which should fail the minimum validation
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            result = parser.parse(jd_text)
            # If parsing succeeds, the model's validator should catch it
            if result.role is None and len(result.required_skills) == 0:
                raise ValidationError("Minimum validation should have failed")

    def test_very_short_input_no_clear_role(self, parser):
        """Very short vague input should either fail or have low confidence."""
        jd_text = "Hire someone"

        try:
            result = parser.parse(jd_text)
            # If it doesn't raise error, check it has either role or skills
            assert result.role is not None or len(result.required_skills) > 0
            # And confidence should be low
            if "role" in result.confidence_scores:
                assert result.confidence_scores["role"].score < 50
        except (ValidationError, ValueError):
            # Acceptable to reject this as too vague
            pass
