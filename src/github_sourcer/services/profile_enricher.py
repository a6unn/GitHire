"""Profile enrichment service.

Combines GitHub user data and repositories into Candidate objects.
"""

import logging
from datetime import datetime
from typing import Optional
from src.github_sourcer.models.candidate import Candidate, Repository
from src.github_sourcer.services.github_client import GitHubClient

logger = logging.getLogger(__name__)


class ProfileNotFoundError(Exception):
    """Raised when a GitHub profile cannot be found."""
    pass


class ProfileEnricher:
    """Enriches GitHub usernames with full profile data."""

    def __init__(self, github_client: GitHubClient):
        """
        Initialize ProfileEnricher.

        Args:
            github_client: GitHubClient instance for API calls
        """
        self.github_client = github_client

    async def enrich_profile(self, username: str) -> Candidate:
        """
        Fetch and enrich a GitHub profile.

        Args:
            username: GitHub username

        Returns:
            Candidate object with full profile data

        Raises:
            ProfileNotFoundError: If profile not found (404)
        """
        # Fetch user profile
        profile_data = await self.github_client.get_profile(username)

        if profile_data is None:
            raise ProfileNotFoundError(f"Profile not found: {username}")

        # Fetch repositories
        repos_data = await self.github_client.get_repos(username)

        # Build Candidate object
        candidate = self._build_candidate(profile_data, repos_data)

        logger.debug(f"Enriched profile for {username}: {len(candidate.top_repos)} repos, {len(candidate.languages)} languages")

        return candidate

    def _build_candidate(self, profile: dict, repos: list[dict]) -> Candidate:
        """
        Build Candidate object from GitHub API data.

        Args:
            profile: User profile dict from GitHub API
            repos: List of repository dicts from GitHub API

        Returns:
            Candidate object
        """
        # Extract top 5 repos by stars
        top_repos = self._extract_top_repos(repos)

        # Aggregate languages from all repos
        languages = self._aggregate_languages(repos)

        # Calculate account age
        created_at = profile.get("created_at", "")
        account_age_days = self._calculate_account_age(created_at)

        # Estimate contribution count (simplified - GitHub API doesn't provide this directly)
        # Use public repos count as a proxy
        contribution_count = profile.get("public_repos", 0) * 10  # Rough estimate

        return Candidate(
            github_username=profile["login"],
            name=profile.get("name"),
            github_url=profile["html_url"],  # Required field
            email=profile.get("email"),  # Correct field name (not public_email)
            bio=profile.get("bio"),
            location=profile.get("location"),
            top_repos=top_repos,
            languages=languages,
            contribution_count=contribution_count,
            account_age_days=account_age_days,
            followers=profile.get("followers", 0),
            public_repos=profile.get("public_repos", 0),
            profile_url=profile["html_url"],  # Deprecated but kept for backward compatibility
            avatar_url=profile.get("avatar_url"),
            fetched_at=datetime.utcnow()
        )

    def _extract_top_repos(self, repos: list[dict]) -> list[Repository]:
        """
        Extract top 5 repositories by stars.

        Args:
            repos: List of repository dicts (already sorted by stars)

        Returns:
            List of up to 5 Repository objects
        """
        top_repos = []

        for repo in repos[:5]:  # Already sorted by stars in API call
            # Extract languages (GitHub API only returns primary language)
            languages = []
            if repo.get("language"):
                languages.append(repo["language"])

            repository = Repository(
                name=repo["name"],
                description=repo.get("description"),
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                languages=languages,
                url=repo["html_url"]
            )
            top_repos.append(repository)

        return top_repos

    def _aggregate_languages(self, repos: list[dict]) -> list[str]:
        """
        Aggregate all languages from repositories.

        Args:
            repos: List of repository dicts

        Returns:
            Sorted, deduplicated list of language names
        """
        languages = set()

        for repo in repos:
            lang = repo.get("language")
            if lang:
                languages.add(lang)

        # Return sorted list (deduplication handled by Candidate model validator)
        return sorted(languages)

    def _calculate_account_age(self, created_at: str) -> int:
        """
        Calculate account age in days.

        Args:
            created_at: ISO 8601 timestamp (e.g., "2011-09-03T15:26:22Z")

        Returns:
            Number of days since account creation
        """
        if not created_at:
            return 0

        try:
            # Parse GitHub timestamp
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now(created.tzinfo)
            age = (now - created).days
            return max(0, age)  # Ensure non-negative

        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse created_at: {created_at} - {e}")
            return 0
