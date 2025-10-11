"""Contract tests for Ranking Engine models."""

import pytest
from pydantic import ValidationError

from src.ranking_engine.models import ScoreWeights, ScoreBreakdown, RankedCandidate
from src.github_sourcer.models.candidate import Candidate, Repository


class TestScoreWeights:
    """Test ScoreWeights model validation."""

    def test_default_weights_sum_to_one(self):
        """Test that default weights sum to 1.0."""
        weights = ScoreWeights()
        assert weights.skill_match_weight == 0.40
        assert weights.experience_weight == 0.20
        assert weights.activity_weight == 0.20
        assert weights.domain_weight == 0.20
        total = (
            weights.skill_match_weight +
            weights.experience_weight +
            weights.activity_weight +
            weights.domain_weight
        )
        assert 0.99 <= total <= 1.01

    def test_custom_weights_sum_to_one(self):
        """Test that custom weights can sum to 1.0."""
        weights = ScoreWeights(
            skill_match_weight=0.50,
            experience_weight=0.30,
            activity_weight=0.15,
            domain_weight=0.05
        )
        total = (
            weights.skill_match_weight +
            weights.experience_weight +
            weights.activity_weight +
            weights.domain_weight
        )
        assert 0.99 <= total <= 1.01

    def test_weights_not_summing_to_one_raises_error(self):
        """Test that weights not summing to 1.0 raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ScoreWeights(
                skill_match_weight=0.50,
                experience_weight=0.30,
                activity_weight=0.10,
                domain_weight=0.05  # Total = 0.95, should fail
            )
        assert "must sum to 1.0" in str(exc_info.value)

    def test_weights_exceeding_one_raises_error(self):
        """Test that weights exceeding 1.0 raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ScoreWeights(
                skill_match_weight=0.50,
                experience_weight=0.30,
                activity_weight=0.25,
                domain_weight=0.25  # Total = 1.30, should fail
            )
        assert "must sum to 1.0" in str(exc_info.value)

    def test_negative_weight_raises_error(self):
        """Test that negative weights raise validation error."""
        with pytest.raises(ValidationError):
            ScoreWeights(
                skill_match_weight=-0.10,
                experience_weight=0.50,
                activity_weight=0.30,
                domain_weight=0.30
            )

    def test_weight_above_one_raises_error(self):
        """Test that individual weight > 1.0 raises validation error."""
        with pytest.raises(ValidationError):
            ScoreWeights(
                skill_match_weight=1.50,
                experience_weight=0.0,
                activity_weight=0.0,
                domain_weight=-0.50
            )


class TestScoreBreakdown:
    """Test ScoreBreakdown model validation."""

    def test_valid_score_breakdown(self):
        """Test creating a valid ScoreBreakdown."""
        breakdown = ScoreBreakdown(
            matched_skills=["Python", "FastAPI"],
            missing_skills=["Docker"],
            activity_reasoning="High activity: 500 contributions in last year",
            experience_reasoning="Veteran developer: 7-year account, 100+ stars",
            domain_reasoning="3 fintech projects found"
        )
        assert len(breakdown.matched_skills) == 2
        assert len(breakdown.missing_skills) == 1
        assert "500 contributions" in breakdown.activity_reasoning

    def test_empty_reasoning_raises_error(self):
        """Test that empty reasoning strings raise validation error."""
        with pytest.raises(ValidationError):
            ScoreBreakdown(
                matched_skills=[],
                missing_skills=[],
                activity_reasoning="",  # Should fail
                experience_reasoning="Some reasoning",
                domain_reasoning="Some domain info"
            )

    def test_empty_skill_lists_allowed(self):
        """Test that empty skill lists are allowed."""
        breakdown = ScoreBreakdown(
            matched_skills=[],
            missing_skills=[],
            activity_reasoning="Low activity",
            experience_reasoning="New account",
            domain_reasoning="No domain match"
        )
        assert breakdown.matched_skills == []
        assert breakdown.missing_skills == []


class TestRankedCandidate:
    """Test RankedCandidate model validation."""

    @pytest.fixture
    def sample_candidate(self):
        """Create a sample candidate for testing."""
        return Candidate(
            github_username="testuser",
            name="Test User",
            bio="Test bio",
            location="Test Location",
            followers=100,
            contribution_count=500,
            account_age_days=1825,  # ~5 years
            profile_url="https://github.com/testuser",
            avatar_url="https://avatar.url",
            languages=["Python", "JavaScript"],
            top_repos=[
                Repository(
                    name="test-repo",
                    description="Test repository",
                    stars=100,
                    forks=10,
                    languages=["Python"],
                    url="https://github.com/testuser/test-repo"
                )
            ]
        )

    @pytest.fixture
    def sample_score_breakdown(self):
        """Create a sample score breakdown for testing."""
        return ScoreBreakdown(
            matched_skills=["Python"],
            missing_skills=["Docker"],
            activity_reasoning="Moderate activity",
            experience_reasoning="Mid-level experience",
            domain_reasoning="Some domain match"
        )

    def test_valid_ranked_candidate(self, sample_candidate, sample_score_breakdown):
        """Test creating a valid RankedCandidate."""
        ranked = RankedCandidate(
            candidate=sample_candidate,
            rank=1,
            total_score=75.5,
            skill_match_score=80.0,
            activity_score=70.0,
            experience_score=75.0,
            domain_score=75.0,
            score_breakdown=sample_score_breakdown
        )
        assert ranked.rank == 1
        assert ranked.total_score == 75.5
        assert ranked.github_username == "testuser"

    def test_rank_must_be_positive(self, sample_candidate, sample_score_breakdown):
        """Test that rank must be >= 1."""
        with pytest.raises(ValidationError):
            RankedCandidate(
                candidate=sample_candidate,
                rank=0,  # Should fail
                total_score=75.0,
                skill_match_score=80.0,
                activity_score=70.0,
                experience_score=75.0,
                domain_score=75.0,
                score_breakdown=sample_score_breakdown
            )

    def test_scores_must_be_in_range(self, sample_candidate, sample_score_breakdown):
        """Test that scores must be between 0 and 100."""
        with pytest.raises(ValidationError):
            RankedCandidate(
                candidate=sample_candidate,
                rank=1,
                total_score=150.0,  # Should fail
                skill_match_score=80.0,
                activity_score=70.0,
                experience_score=75.0,
                domain_score=75.0,
                score_breakdown=sample_score_breakdown
            )

    def test_negative_score_raises_error(self, sample_candidate, sample_score_breakdown):
        """Test that negative scores raise validation error."""
        with pytest.raises(ValidationError):
            RankedCandidate(
                candidate=sample_candidate,
                rank=1,
                total_score=75.0,
                skill_match_score=-10.0,  # Should fail
                activity_score=70.0,
                experience_score=75.0,
                domain_score=75.0,
                score_breakdown=sample_score_breakdown
            )

    def test_convenience_properties(self, sample_candidate, sample_score_breakdown):
        """Test convenience properties for accessing candidate data."""
        ranked = RankedCandidate(
            candidate=sample_candidate,
            rank=1,
            total_score=75.0,
            skill_match_score=80.0,
            activity_score=70.0,
            experience_score=75.0,
            domain_score=75.0,
            score_breakdown=sample_score_breakdown
        )
        assert ranked.github_username == "testuser"
        assert ranked.name == "Test User"
        assert str(ranked.profile_url) == "https://github.com/testuser"
