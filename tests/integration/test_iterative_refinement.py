"""Integration test for Scenario 6: Iterative refinement (re-parsing)."""

import pytest
from src.jd_parser.parser import JDParser


class TestIterativeRefinement:
    """Test that parser handles iterative refinement (editing and re-parsing)."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_reparse_after_edit_produces_different_result(self, parser):
        """
        Scenario 6: Re-parsing edited JD should reflect changes.

        First parse: "React developer"
        Second parse: "React developer with 3+ years experience"

        Expected: Second result includes years_of_experience.min = 3
        """
        # First parse
        jd_v1 = "React developer"
        result_v1 = parser.parse(jd_v1)

        assert result_v1.years_of_experience.min is None

        # Second parse (edited)
        jd_v2 = "React developer with 3+ years experience"
        result_v2 = parser.parse(jd_v2)

        assert result_v2.years_of_experience.min == 3

        # Both should have React skill
        assert "react" in [s.lower() for s in result_v1.required_skills]
        assert "react" in [s.lower() for s in result_v2.required_skills]

    def test_parser_is_stateless(self, parser):
        """Parser should be stateless (no cross-contamination between parses)."""
        jd1 = "Python developer with Django experience"
        jd2 = "Java developer with Spring Boot"

        result1 = parser.parse(jd1)
        result2 = parser.parse(jd2)

        # Results should be independent
        assert "python" in [s.lower() for s in result1.required_skills]
        assert "java" in [s.lower() for s in result2.required_skills]

        # First result should not have Java
        assert "java" not in [s.lower() for s in result1.required_skills]
        # Second result should not have Python
        assert "python" not in [s.lower() for s in result2.required_skills]
