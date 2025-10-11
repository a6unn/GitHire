"""Integration tests for experience scorer."""

import pytest
from src.github_sourcer.models.candidate import Candidate, Repository
from src.ranking_engine.scorers.experience_scorer import ExperienceScorer


class TestExperienceScorer:
    """Test experience scoring based on account age, stars, and repos."""

    def create_candidate(
        self,
        age_days: int,
        repos_with_stars: list[tuple[str, int]]
    ) -> Candidate:
        """Helper to create a candidate with specific age and repos."""
        repos = [
            Repository(
                name=name,
                description=f"{name} description",
                stars=stars,
                forks=0,
                languages=["Python"],
                url=f"https://github.com/test/{name}"
            )
            for name, stars in repos_with_stars
        ]

        return Candidate(
            github_username="testuser",
            account_age_days=age_days,
            contribution_count=0,
            profile_url="https://github.com/testuser",
            top_repos=repos
        )

    def test_new_account_low_score(self):
        """Test brand new account (1 month) gets low score."""
        scorer = ExperienceScorer()

        # 1 month old, no stars, 1 repo
        candidate = self.create_candidate(
            age_days=30,
            repos_with_stars=[("repo1", 0)]
        )

        score, reasoning = scorer.score(candidate)

        # New account should get low score (< 30)
        assert score < 30
        assert "1-month account" in reasoning
        assert "no stars" in reasoning or "0 stars" in reasoning

    def test_veteran_account_high_score(self):
        """Test veteran account (7 years) gets high score."""
        scorer = ExperienceScorer()

        # 7 years old, 1000+ stars, 5 repos
        candidate = self.create_candidate(
            age_days=2555,  # ~7 years
            repos_with_stars=[
                ("repo1", 500),
                ("repo2", 300),
                ("repo3", 200),
                ("repo4", 50),
                ("repo5", 50)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Veteran with high stars should get high score (> 80)
        assert score > 80
        assert "7.0-year account" in reasoning
        assert "stars" in reasoning

    def test_mid_level_experience(self):
        """Test mid-level developer (3 years, moderate stars)."""
        scorer = ExperienceScorer()

        # 3 years old, 150 stars, 5 repos
        candidate = self.create_candidate(
            age_days=1095,  # 3 years exactly
            repos_with_stars=[
                ("repo1", 50),
                ("repo2", 40),
                ("repo3", 30),
                ("repo4", 20),
                ("repo5", 10)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Mid-level should get moderate score (50-75)
        assert 50 < score < 75
        assert "3.0-year account" in reasoning

    def test_high_stars_boost_score(self):
        """Test that high stars boost score significantly."""
        scorer = ExperienceScorer()

        # 2 year account but 5000+ stars
        candidate = self.create_candidate(
            age_days=730,  # 2 years
            repos_with_stars=[
                ("popular-repo", 5000)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # High stars should boost score despite moderate age
        # Score = age(~45) * 0.4 + stars(100) * 0.3 + repos(50) * 0.3 = ~48
        assert score > 45
        assert "5000+ stars" in reasoning or "5000 stars" in reasoning
        assert "highly popular" in reasoning

    def test_many_repos_boost_score(self):
        """Test that many repos (with stars) boost score."""
        scorer = ExperienceScorer()

        # 2 years, 5 repos with decent stars each
        candidate = self.create_candidate(
            age_days=730,
            repos_with_stars=[
                ("repo1", 100),
                ("repo2", 80),
                ("repo3", 60),
                ("repo4", 40),
                ("repo5", 20)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Multiple quality repos should boost score
        assert score > 60
        assert "5+ repositories" in reasoning

    def test_no_repos_low_score(self):
        """Test candidate with no repos gets low score."""
        scorer = ExperienceScorer()

        # 5 years old but no repos
        candidate = self.create_candidate(
            age_days=1825,  # 5 years
            repos_with_stars=[]
        )

        score, reasoning = scorer.score(candidate)

        # No repos should lower score despite old account
        assert score < 60  # Age helps but no repos/stars hurts
        assert "no repositories" in reasoning
        assert "no stars" in reasoning

    def test_few_stars_low_score(self):
        """Test candidate with very few stars."""
        scorer = ExperienceScorer()

        # 1 year, 5 stars total
        candidate = self.create_candidate(
            age_days=365,
            repos_with_stars=[
                ("repo1", 3),
                ("repo2", 2)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Few stars should result in lower score
        assert score < 50
        assert "5 stars" in reasoning

    def test_composite_scoring(self):
        """Test that composite score balances all factors."""
        scorer = ExperienceScorer()

        # Old account (5 years), moderate stars (50), few repos (2)
        candidate = self.create_candidate(
            age_days=1825,  # 5 years
            repos_with_stars=[
                ("repo1", 30),
                ("repo2", 20)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Should be moderate score (account age helps, but low stars/repos)
        assert 50 < score < 75
        assert "5.0-year account" in reasoning

    def test_junior_developer_profile(self):
        """Test typical junior developer profile."""
        scorer = ExperienceScorer()

        # 1 year, 20 stars, 3 repos
        candidate = self.create_candidate(
            age_days=365,
            repos_with_stars=[
                ("project1", 10),
                ("project2", 7),
                ("project3", 3)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Junior profile should get modest score (25-50)
        # Score = age(30) * 0.4 + stars(~40) * 0.3 + repos(24) * 0.3 = ~29
        assert 25 < score < 50
        assert "1.0-year account" in reasoning
        assert "20 stars" in reasoning

    def test_senior_developer_profile(self):
        """Test typical senior developer profile."""
        scorer = ExperienceScorer()

        # 6 years, 500 stars, 5 repos
        candidate = self.create_candidate(
            age_days=2190,  # 6 years
            repos_with_stars=[
                ("major-project", 300),
                ("tool", 100),
                ("library", 50),
                ("demo", 30),
                ("experiment", 20)
            ]
        )

        score, reasoning = scorer.score(candidate)

        # Senior profile should get high score (75-95)
        assert 75 < score < 95
        assert "6.0-year account" in reasoning
        assert "500 stars" in reasoning
        assert "well-recognized" in reasoning
