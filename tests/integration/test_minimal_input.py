"""Integration test for Scenario 2: Minimal input parsing."""

import pytest
from src.jd_parser.parser import JDParser


class TestMinimalInput:
    """Test parsing minimal JD with just skill or role."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_parse_minimal_skill_only(self, parser):
        """
        Scenario 2: Parse minimal input with only a skill mentioned.

        Input: "React developer"

        Expected:
        - role: "React Developer" or similar
        - required_skills: ["React"] (normalized)
        - Most other fields: None or empty
        - Still passes minimum validation (has role OR skill)
        """
        jd_text = "React developer"

        result = parser.parse(jd_text)

        # Should extract either role or skill (or both)
        assert result.role is not None or len(result.required_skills) > 0

        # Should normalize "React"
        if len(result.required_skills) > 0:
            skills_lower = [s.lower() for s in result.required_skills]
            assert "react" in skills_lower or "reactjs" in skills_lower

        # Optional fields can be None/empty
        assert result.years_of_experience.min is None or result.years_of_experience.min >= 0
        assert result.seniority_level is None or result.seniority_level in [
            "Junior", "Mid-level", "Senior", "Staff", "Principal"
        ]

        # Original input preserved
        assert result.original_input == jd_text

    def test_parse_role_only(self, parser):
        """Parse minimal input with only role, no skills."""
        jd_text = "Software Engineer needed"

        result = parser.parse(jd_text)

        # Must have role (since no skills mentioned)
        assert result.role is not None
        assert "engineer" in result.role.lower() or "software" in result.role.lower()

        # Skills might be empty for vague roles
        assert isinstance(result.required_skills, list)

        # Confidence might be lower for vague inputs
        if "role" in result.confidence_scores:
            assert result.confidence_scores["role"].score >= 0
