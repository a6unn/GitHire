"""Activity scoring based on GitHub activity metrics."""

import logging
from src.github_sourcer.models.candidate import Candidate

logger = logging.getLogger(__name__)


class ActivityScorer:
    """Calculates activity score based on followers and contribution count."""

    def score(self, candidate: Candidate) -> tuple[float, str]:
        """
        Calculate activity score from candidate's GitHub activity.

        Args:
            candidate: Candidate with GitHub profile data

        Returns:
            Tuple of (score 0-100, reasoning string)

        Scoring formula (weighted average):
            - Followers: 40% (0-10 → 0-30, 10-100 → 30-60, 100-1000 → 60-85, 1000+ → 85-100)
            - Contribution count: 40% (0-100 → 0-30, 100-500 → 30-70, 500-2000 → 70-90, 2000+ → 90-100)
            - Public repos: 20% (0-5 → 0-40, 5-20 → 40-70, 20+ → 70-100)
        """
        # Calculate individual scores
        followers_score = self._score_followers(candidate.followers)
        contribution_score = self._score_contributions(candidate.contribution_count)
        repos_score = self._score_repos(len(candidate.top_repos))

        # Weighted combination
        total_score = (
            followers_score * 0.40 +
            contribution_score * 0.40 +
            repos_score * 0.20
        )

        # Build reasoning string
        reasoning = self._build_reasoning(
            candidate.followers,
            candidate.contribution_count,
            len(candidate.top_repos)
        )

        logger.debug(
            f"Activity score for {candidate.github_username}: {total_score:.1f} "
            f"(followers={followers_score:.1f}, contributions={contribution_score:.1f}, repos={repos_score:.1f})"
        )

        return (total_score, reasoning)

    def _score_followers(self, followers: int) -> float:
        """
        Score follower count (0-100).

        Ranges:
            - 0-10 followers: 0-30 points (limited reach)
            - 10-100 followers: 30-60 points (growing community)
            - 100-1000 followers: 60-85 points (recognized developer)
            - 1000+ followers: 85-100 points (influential developer)
        """
        if followers < 10:
            return (followers / 10) * 30
        elif followers < 100:
            followers_over_ten = (followers - 10) / (100 - 10)
            return 30 + (followers_over_ten * 30)
        elif followers < 1000:
            followers_over_hundred = (followers - 100) / (1000 - 100)
            return 60 + (followers_over_hundred * 25)
        else:
            followers_over_thousand = (followers - 1000) / 10000
            return min(100, 85 + (followers_over_thousand * 15))

    def _score_contributions(self, contributions: int) -> float:
        """
        Score contribution count (0-100).

        Ranges:
            - 0-100 contributions: 0-30 points (occasional contributor)
            - 100-500 contributions: 30-70 points (regular contributor)
            - 500-2000 contributions: 70-90 points (active contributor)
            - 2000+ contributions: 90-100 points (very active contributor)
        """
        if contributions < 100:
            return (contributions / 100) * 30
        elif contributions < 500:
            contrib_over_hundred = (contributions - 100) / (500 - 100)
            return 30 + (contrib_over_hundred * 40)
        elif contributions < 2000:
            contrib_over_500 = (contributions - 500) / (2000 - 500)
            return 70 + (contrib_over_500 * 20)
        else:
            contrib_over_2000 = (contributions - 2000) / 10000
            return min(100, 90 + (contrib_over_2000 * 10))

    def _score_repos(self, repo_count: int) -> float:
        """
        Score public repository count (0-100).

        Ranges:
            - 0-5 repos: 0-40 points
            - 5-20 repos: 40-70 points
            - 20+ repos: 70-100 points
        """
        if repo_count < 5:
            return (repo_count / 5) * 40
        elif repo_count < 20:
            repos_over_five = (repo_count - 5) / (20 - 5)
            return 40 + (repos_over_five * 30)
        else:
            return min(100, 70 + ((repo_count - 20) / 30) * 30)

    def _build_reasoning(
        self,
        followers: int,
        contributions: int,
        repo_count: int
    ) -> str:
        """Build human-readable reasoning string."""
        # Followers
        if followers == 0:
            followers_desc = "0 followers"
        elif followers < 10:
            followers_desc = f"{followers} followers"
        elif followers < 100:
            followers_desc = f"{followers} followers (growing community)"
        elif followers < 1000:
            followers_desc = f"{followers} followers (recognized)"
        else:
            followers_desc = f"{followers}+ followers (influential)"

        # Contributions
        if contributions < 100:
            contrib_desc = f"{contributions} contributions"
        elif contributions < 500:
            contrib_desc = f"{contributions} contributions (regular)"
        elif contributions < 2000:
            contrib_desc = f"{contributions} contributions (active)"
        else:
            contrib_desc = f"{contributions}+ contributions (very active)"

        # Repos
        repo_desc = f"{repo_count} repositories"

        return f"{followers_desc}, {contrib_desc}, {repo_desc}"
