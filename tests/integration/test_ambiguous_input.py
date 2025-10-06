"""Integration test for Scenario 4: Ambiguous input with low confidence."""

import pytest
from src.jd_parser.parser import JDParser


class TestAmbiguousInput:
    """Test parsing ambiguous JDs that should result in low confidence scores."""

    @pytest.fixture
    def parser(self):
        """Initialize JD Parser."""
        return JDParser()

    def test_vague_jd_has_low_confidence(self, parser):
        """
        Scenario 4: Vague JD should parse but have low confidence scores.

        Input: "Need developer ASAP for project work"

        Expected:
        - Should extract something (role: "Developer")
        - Confidence scores < 60% due to vagueness
        - Missing fields flagged with low confidence
        """
        jd_text = "Need developer ASAP for project work"

        result = parser.parse(jd_text)

        # Should extract minimal info
        assert result.role is not None or len(result.required_skills) > 0

        # Confidence should be low for vague input
        assert len(result.confidence_scores) > 0
        avg_confidence = sum(cs.score for cs in result.confidence_scores.values()) / len(result.confidence_scores)
        assert avg_confidence < 60, "Vague input should have low average confidence"

    def test_contradictory_input_flagged(self, parser):
        """Contradictory requirements should still parse but flag ambiguity."""
        jd_text = "Junior developer with 10+ years of experience in AI/ML"

        result = parser.parse(jd_text)

        # Should extract both contradictory pieces
        assert result.seniority_level == "Junior"
        assert result.years_of_experience.min >= 10

        # Confidence for seniority should be low due to contradiction
        if "seniority_level" in result.confidence_scores:
            assert result.confidence_scores["seniority_level"].score < 70
