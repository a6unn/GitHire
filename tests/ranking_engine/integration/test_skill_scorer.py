"""Integration tests for skill scorer."""

import pytest

from src.ranking_engine.scorers.skill_scorer import SkillScorer


class TestSkillScorer:
    """Test skill match percentage scoring."""

    def test_zero_percent_match(self):
        """Test 0% match (0 of 5 skills)."""
        scorer = SkillScorer()

        matched = []
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 0.0

    def test_twenty_percent_match(self):
        """Test 20% match (1 of 5 skills)."""
        scorer = SkillScorer()

        matched = ["Python"]
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 20.0

    def test_forty_percent_match(self):
        """Test 40% match (2 of 5 skills)."""
        scorer = SkillScorer()

        matched = ["Python", "Docker"]
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 40.0

    def test_sixty_percent_match(self):
        """Test 60% match (3 of 5 skills)."""
        scorer = SkillScorer()

        matched = ["Python", "Docker", "FastAPI"]
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 60.0

    def test_eighty_percent_match(self):
        """Test 80% match (4 of 5 skills)."""
        scorer = SkillScorer()

        matched = ["Python", "Docker", "FastAPI", "PostgreSQL"]
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 80.0

    def test_hundred_percent_match(self):
        """Test 100% match (5 of 5 skills)."""
        scorer = SkillScorer()

        matched = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]
        required = ["Python", "Docker", "Kubernetes", "FastAPI", "PostgreSQL"]

        score = scorer.score(matched, required)

        assert score == 100.0

    def test_empty_required_skills(self):
        """Test with no required skills returns 100%."""
        scorer = SkillScorer()

        matched = []
        required = []

        score = scorer.score(matched, required)

        # No requirements = perfect match
        assert score == 100.0

    def test_fifty_percent_match(self):
        """Test 50% match (1 of 2 skills)."""
        scorer = SkillScorer()

        matched = ["Python"]
        required = ["Python", "JavaScript"]

        score = scorer.score(matched, required)

        assert score == 50.0

    def test_thirty_three_percent_match(self):
        """Test 33.33% match (1 of 3 skills)."""
        scorer = SkillScorer()

        matched = ["Python"]
        required = ["Python", "JavaScript", "Go"]

        score = scorer.score(matched, required)

        assert abs(score - 33.333333) < 0.001  # Floating point comparison

    def test_single_skill_match(self):
        """Test single required skill matched."""
        scorer = SkillScorer()

        matched = ["Python"]
        required = ["Python"]

        score = scorer.score(matched, required)

        assert score == 100.0

    def test_single_skill_no_match(self):
        """Test single required skill not matched."""
        scorer = SkillScorer()

        matched = []
        required = ["Python"]

        score = scorer.score(matched, required)

        assert score == 0.0
