"""Integration test for Scenario 5: Formal multi-paragraph JD."""

import pytest
from src.jd_parser.parser import JDParser


class TestFormalJD:
    """Test parsing formal job descriptions with multiple sections."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_parse_formal_multi_section_jd(self, parser):
        """
        Scenario 5: Parse formal JD with sections (About Us, Requirements, Benefits).

        Expected: Extract relevant info from Requirements section, ignore noise.
        """
        jd_text = """About Us:
        We are a leading fintech company revolutionizing payments.

        Job Requirements:
        - 7+ years of experience in backend development
        - Strong proficiency in Go, Kubernetes, and PostgreSQL
        - Experience with microservices architecture required
        - Knowledge of AWS is a plus

        What We Offer:
        - Competitive salary
        - Remote-first culture
        - Health insurance
        """

        result = parser.parse(jd_text)

        # Should extract from Requirements section
        assert "go" in [s.lower() for s in result.required_skills] or \
               "golang" in [s.lower() for s in result.required_skills]
        assert result.years_of_experience.min == 7

        # Should identify preferred vs required
        assert "kubernetes" in [s.lower() for s in result.required_skills] or \
               "k8s" in [s.lower() for s in result.required_skills]

        # Benefits section should be ignored
        assert "health insurance" not in result.required_skills
        assert "competitive salary" not in result.required_skills
