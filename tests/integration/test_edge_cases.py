"""Integration test for Scenario 7: Edge cases."""

import pytest
from src.jd_parser.parser import JDParser
from pydantic import ValidationError


class TestEdgeCases:
    """Test edge cases: contradictions, typos, non-English, long input."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_typos_in_skills_still_normalized(self, parser):
        """Typos in skill names should be normalized by LLM."""
        jd_text = "Looking for developer with experince in Reactt and Postgre SQL"

        result = parser.parse(jd_text)

        # LLM should correct typos during extraction
        skills_lower = [s.lower() for s in result.required_skills]
        assert "react" in skills_lower or "reactjs" in skills_lower
        assert "postgresql" in skills_lower or "postgres" in skills_lower

    def test_very_long_input_truncated_or_handled(self, parser):
        """Very long JD (1000+ words) should be handled gracefully."""
        # Generate long JD by repeating content
        base_jd = "Senior Python developer with FastAPI and PostgreSQL. "
        long_jd = base_jd * 200  # ~1000 words

        result = parser.parse(long_jd)

        # Should still extract core info
        assert "python" in [s.lower() for s in result.required_skills]
        assert result.seniority_level == "Senior"

    def test_mixed_english_text_extracts_english_only(self, parser):
        """
        Input with mixed non-English words should extract English parts.

        Per FR-001: Only English supported, but LLM should handle occasional non-English words.
        """
        jd_text = "Senior développeur Python avec 5 ans d'expérience (5 years experience in Python)"

        result = parser.parse(jd_text)

        # Should extract from English portions
        assert "python" in [s.lower() for s in result.required_skills]
        assert result.years_of_experience.min == 5

    def test_contradictory_requirements_both_extracted(self, parser):
        """Contradictory info should be extracted as-is (no resolution)."""
        jd_text = "Junior developer with 10 years of expert-level experience"

        result = parser.parse(jd_text)

        # Both contradictory elements should be present
        assert result.seniority_level == "Junior"
        assert result.years_of_experience.min >= 10

        # Confidence should reflect ambiguity
        if "seniority_level" in result.confidence_scores and \
           "years_of_experience" in result.confidence_scores:
            # At least one should have lower confidence
            assert min(
                result.confidence_scores["seniority_level"].score,
                result.confidence_scores["years_of_experience"].score
            ) < 75

    def test_special_characters_handled(self, parser):
        """Special characters, emojis, etc. should be handled."""
        jd_text = "🚀 Looking for a 🐍 Python dev with ⚡ FastAPI skills! (2+ years)"

        result = parser.parse(jd_text)

        # Should extract despite emojis
        assert "python" in [s.lower() for s in result.required_skills]
        assert "fastapi" in [s.lower() for s in result.required_skills]
        assert result.years_of_experience.min == 2

    def test_all_caps_normalized(self, parser):
        """ALL CAPS input should be normalized."""
        jd_text = "SENIOR PYTHON DEVELOPER WITH DJANGO EXPERIENCE"

        result = parser.parse(jd_text)

        assert result.seniority_level == "Senior"
        assert "python" in [s.lower() for s in result.required_skills]
        assert "django" in [s.lower() for s in result.required_skills]
