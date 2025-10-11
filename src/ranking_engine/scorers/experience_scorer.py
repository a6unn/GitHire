"""Experience scoring based on GitHub account history."""

import logging
from src.github_sourcer.models.candidate import Candidate

logger = logging.getLogger(__name__)


class ExperienceScorer:
    """Calculates experience score based on account age, stars, and repo count."""

    def score(self, candidate: Candidate) -> tuple[float, str]:
        """
        Calculate experience score from candidate's GitHub history.

        Args:
            candidate: Candidate with GitHub profile data

        Returns:
            Tuple of (score 0-100, reasoning string)

        Scoring formula (weighted average):
            - Account age: 40% (0-365 days → 0-30, 1-3 years → 30-60, 3-5 years → 60-80, 5+ years → 80-100)
            - Total stars: 30% (0-10 → 0-30, 10-100 → 30-70, 100-1000 → 70-90, 1000+ → 90-100)
            - Repo count: 30% (0-5 → 0-40, 5-20 → 40-70, 20-50 → 70-90, 50+ → 90-100)
        """
        # Calculate individual scores
        age_score = self._score_account_age(candidate.account_age_days)
        stars_score = self._score_total_stars(candidate)
        repo_score = self._score_repo_count(candidate)

        # Weighted combination
        total_score = (
            age_score * 0.40 +
            stars_score * 0.30 +
            repo_score * 0.30
        )

        # Build reasoning string
        reasoning = self._build_reasoning(
            candidate.account_age_days,
            candidate.top_repos,
            len(candidate.top_repos),
            age_score,
            stars_score,
            repo_score
        )

        logger.debug(
            f"Experience score for {candidate.github_username}: {total_score:.1f} "
            f"(age={age_score:.1f}, stars={stars_score:.1f}, repos={repo_score:.1f})"
        )

        return (total_score, reasoning)

    def _score_account_age(self, age_days: int) -> float:
        """
        Score account age (0-100).

        Ranges:
            - 0-365 days (< 1 year): 0-30 points (junior/new account)
            - 365-1095 days (1-3 years): 30-60 points (early career)
            - 1095-1825 days (3-5 years): 60-80 points (mid-level)
            - 1825+ days (5+ years): 80-100 points (senior/veteran)
        """
        if age_days < 365:
            # 0-1 year: linear scale 0-30
            return (age_days / 365) * 30
        elif age_days < 1095:  # 3 years
            # 1-3 years: linear scale 30-60
            years_over_one = (age_days - 365) / (1095 - 365)
            return 30 + (years_over_one * 30)
        elif age_days < 1825:  # 5 years
            # 3-5 years: linear scale 60-80
            years_over_three = (age_days - 1095) / (1825 - 1095)
            return 60 + (years_over_three * 20)
        else:
            # 5+ years: linear scale 80-100, cap at 100
            years_over_five = (age_days - 1825) / 1825
            return min(100, 80 + (years_over_five * 20))

    def _score_total_stars(self, candidate: Candidate) -> float:
        """
        Score total stars across all repos (0-100).

        Ranges:
            - 0-10 stars: 0-30 points (beginner projects)
            - 10-100 stars: 30-70 points (some recognition)
            - 100-1000 stars: 70-90 points (well-recognized projects)
            - 1000+ stars: 90-100 points (highly recognized/popular)
        """
        total_stars = sum(repo.stars for repo in candidate.top_repos)

        if total_stars < 10:
            # 0-10 stars: linear scale 0-30
            return (total_stars / 10) * 30
        elif total_stars < 100:
            # 10-100 stars: linear scale 30-70
            stars_over_ten = (total_stars - 10) / (100 - 10)
            return 30 + (stars_over_ten * 40)
        elif total_stars < 1000:
            # 100-1000 stars: linear scale 70-90
            stars_over_hundred = (total_stars - 100) / (1000 - 100)
            return 70 + (stars_over_hundred * 20)
        else:
            # 1000+ stars: linear scale 90-100, cap at 100
            stars_over_thousand = (total_stars - 1000) / 10000
            return min(100, 90 + (stars_over_thousand * 10))

    def _score_repo_count(self, candidate: Candidate) -> float:
        """
        Score repository count (0-100).

        Note: We only have top_repos (max 5), so we use that as proxy.
        In real scenario with full profile, we'd use public_repos count.

        Ranges:
            - 0-5 repos: 0-40 points (few projects)
            - 5-20 repos: 40-70 points (moderate portfolio)
            - 20-50 repos: 70-90 points (extensive portfolio)
            - 50+ repos: 90-100 points (very active developer)
        """
        repo_count = len(candidate.top_repos)

        # Since we only have top 5, estimate based on what we have
        # If they have 5 top repos with good stars, they likely have more
        if repo_count == 0:
            return 0
        elif repo_count < 5:
            # 0-5 repos: linear scale 0-40
            return (repo_count / 5) * 40
        else:
            # 5 repos (our max): assume moderate portfolio
            # Give 50-70 points based on star quality
            avg_stars = sum(repo.stars for repo in candidate.top_repos) / repo_count
            if avg_stars < 10:
                return 50
            elif avg_stars < 50:
                return 60
            else:
                return 70

    def _build_reasoning(
        self,
        age_days: int,
        repos: list,
        repo_count: int,
        age_score: float,
        stars_score: float,
        repo_score: float
    ) -> str:
        """Build human-readable reasoning string."""
        # Account age
        years = age_days / 365
        if years < 1:
            age_desc = f"{int(age_days/30)}-month account"
        else:
            age_desc = f"{years:.1f}-year account"

        # Total stars
        total_stars = sum(repo.stars for repo in repos)
        if total_stars == 0:
            stars_desc = "no stars"
        elif total_stars < 10:
            stars_desc = f"{total_stars} stars"
        elif total_stars < 100:
            stars_desc = f"{total_stars} stars (some recognition)"
        elif total_stars < 1000:
            stars_desc = f"{total_stars} stars (well-recognized)"
        else:
            stars_desc = f"{total_stars}+ stars (highly popular)"

        # Repo count
        if repo_count == 0:
            repo_desc = "no repositories"
        elif repo_count < 5:
            repo_desc = f"{repo_count} repositories"
        else:
            repo_desc = f"{repo_count}+ repositories"

        return f"{age_desc}, {stars_desc}, {repo_desc}"
