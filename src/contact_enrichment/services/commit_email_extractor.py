"""
Commit Email Extractor Service (Layer 2)
Module 010: Contact Enrichment

Extracts email addresses from commit history (public events API).
Success rate: 41.7% email (validated)
"""

import httpx
from typing import Optional
from ..lib.email_deduplicator import EmailDeduplicator


class CommitEmailExtractor:
    """
    Layer 2: Extract email addresses from commit author history.

    Uses GitHub Events API to get recent commits and extract author emails.

    Constitutional Rules:
    - CR-001: Privacy-First - Filters noreply emails (user chose to hide)
    - CR-004: Transparency - Records source as 'commit'
    """

    def __init__(self, github_token: str):
        """
        Initialize commit email extractor.

        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token
        self.deduplicator = EmailDeduplicator()

    async def _fetch_github_events(self, username: str) -> Optional[list[dict]]:
        """
        Fetch GitHub events data from API.

        Args:
            username: GitHub username

        Returns:
            List of events or None if failed
        """
        url = f"https://api.github.com/users/{username}/events"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        # Add auth token if not test token
        if self.github_token and self.github_token != "test_token":
            headers["Authorization"] = f"token {self.github_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # User not found
                    return None
                else:
                    # Other errors (rate limit, etc.)
                    return None
        except Exception:
            # Network errors, timeouts, etc.
            return None

    async def extract(self, username: str, events_data: Optional[list[dict]] = None, fetch_fresh: bool = False) -> list[str]:
        """
        Extract unique, valid emails from commit history.

        Args:
            username: GitHub username
            events_data: GitHub API /users/{username}/events response (optional)
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            List of deduplicated, validated emails
        """
        # Fetch fresh data if requested or if no data provided
        if fetch_fresh or events_data is None:
            fresh_data = await self._fetch_github_events(username)
            if fresh_data:
                events_data = fresh_data

        if not events_data:
            return []

        emails = []

        # Process each event
        for event in events_data:
            # Only process PushEvent (contains commits)
            if event.get("type") != "PushEvent":
                continue

            # Extract commits from payload
            payload = event.get("payload", {})
            commits = payload.get("commits", [])

            for commit in commits:
                # Extract author email (handle missing author gracefully)
                author = commit.get("author", {})
                email = author.get("email")

                if email:
                    emails.append(email)

        # Deduplicate and filter (handles noreply, spam, invalid)
        return self.deduplicator.deduplicate(emails)

    async def extract_with_sources(
        self, username: str, events_data: Optional[list[dict]] = None, fetch_fresh: bool = False
    ) -> list[tuple[str, str]]:
        """
        Extract emails with source information.

        Args:
            username: GitHub username
            events_data: GitHub API /users/{username}/events response (optional)
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            List of (email, source) tuples where source='commit'
        """
        emails = await self.extract(username, events_data, fetch_fresh)
        return [(email, "commit") for email in emails]
