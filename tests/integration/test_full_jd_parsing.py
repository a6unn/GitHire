"""Integration test for Scenario 1: Full JD parsing with rich context."""

import pytest
from src.jd_parser.parser import JDParser


class TestFullJDParsing:
    """Test parsing a complete job description with multiple fields."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser (will fail until implemented)."""
        return JDParser()

    def test_parse_senior_python_fintech_jd(self, parser):
        """
        Scenario 1: Parse a detailed JD with role, skills, experience, location, and domain.

        Input: "We are seeking a Senior Python Developer with 5+ years of experience
                in the fintech industry. Must have expertise in FastAPI, PostgreSQL,
                and microservices architecture. Experience with Docker and Kubernetes
                is a plus. Remote work available, preference for candidates in
                Tamil Nadu or Bangalore."

        Expected:
        - role: "Senior Python Developer"
        - required_skills: ["Python", "FastAPI", "PostgreSQL", "Microservices"]
        - preferred_skills: ["Docker", "Kubernetes"]
        - years_of_experience.min: 5
        - seniority_level: "Senior"
        - location_preferences: ["Remote", "Tamil Nadu", "Bangalore"]
        - domain: "Fintech"
        - confidence_scores: All fields > 70%
        """
        jd_text = """We are seeking a Senior Python Developer with 5+ years of experience
        in the fintech industry. Must have expertise in FastAPI, PostgreSQL, and
        microservices architecture. Experience with Docker and Kubernetes is a plus.
        Remote work available, preference for candidates in Tamil Nadu or Bangalore."""

        result = parser.parse(jd_text)

        # Validate structure
        assert result.role is not None
        assert "Python" in result.role or "python" in result.role.lower()
        assert "Senior" in result.role

        # Validate required skills (normalized)
        assert "python" in [s.lower() for s in result.required_skills]
        assert "fastapi" in [s.lower() for s in result.required_skills]
        assert "postgresql" in [s.lower() for s in result.required_skills] or \
               "postgres" in [s.lower() for s in result.required_skills]

        # Validate preferred skills
        assert len(result.preferred_skills) > 0
        pref_lower = [s.lower() for s in result.preferred_skills]
        assert "docker" in pref_lower or "kubernetes" in pref_lower

        # Validate experience
        assert result.years_of_experience.min == 5
        assert result.years_of_experience.range_text is not None

        # Validate seniority
        assert result.seniority_level == "Senior"

        # Validate location
        assert len(result.location_preferences) > 0
        locations_lower = [loc.lower() for loc in result.location_preferences]
        assert any("tamil nadu" in loc or "bangalore" in loc or "remote" in loc
                   for loc in locations_lower)

        # Validate domain
        assert result.domain is not None
        assert "fintech" in result.domain.lower()

        # Validate confidence scores exist
        assert len(result.confidence_scores) > 0
        assert "role" in result.confidence_scores
        assert result.confidence_scores["role"].score > 70

        # Validate original input preserved
        assert result.original_input == jd_text

        # Validate schema version
        assert result.schema_version == "1.0.0"
