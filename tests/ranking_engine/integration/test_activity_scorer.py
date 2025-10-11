"""Integration tests for activity scorer."""

import pytest
from src.github_sourcer.models.candidate import Candidate, Repository
from src.ranking_engine.scorers.activity_scorer import ActivityScorer


class TestActivityScorer:
    """Test activity scoring."""

    def create_candidate(self, followers: int, contributions: int, repo_count: int) -> Candidate:
        """Helper to create a candidate."""
        repos = [
            Repository(
                name=f"repo{i}",
                description="Test repo",
                stars=0,
                forks=0,
                languages=["Python"],
                url=f"https://github.com/test/repo{i}"
            )
            for i in range(repo_count)
        ]

        return Candidate(
            github_username="testuser",
            followers=followers,
            contribution_count=contributions,
            account_age_days=365,
            profile_url="https://github.com/testuser",
            top_repos=repos
        )

    def test_high_activity(self):
        """Test high activity profile."""
        scorer = ActivityScorer()
        candidate = self.create_candidate(followers=5000, contributions=3000, repo_count=50)
        score, reasoning = scorer.score(candidate)
        assert score > 80  # High activity should get > 80
        assert "5000+ followers" in reasoning or "5000 followers" in reasoning

    def test_low_activity(self):
        """Test low activity profile."""
        scorer = ActivityScorer()
        candidate = self.create_candidate(followers=5, contributions=50, repo_count=2)
        score, reasoning = scorer.score(candidate)
        assert score < 40

    def test_moderate_activity(self):
        """Test moderate activity profile."""
        scorer = ActivityScorer()
        candidate = self.create_candidate(followers=100, contributions=500, repo_count=10)
        score, reasoning = scorer.score(candidate)
        assert 50 < score < 80

    def test_zero_activity(self):
        """Test zero activity."""
        scorer = ActivityScorer()
        candidate = self.create_candidate(followers=0, contributions=0, repo_count=0)
        score, reasoning = scorer.score(candidate)
        assert score == 0.0
        assert "0 followers" in reasoning
