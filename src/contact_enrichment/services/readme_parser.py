"""
README Parser Service (Layer 3)
Module 010: Contact Enrichment

Parses profile README (username/username repo) for contact information.
Success rate: 50% README coverage (validated)
"""

import base64
import httpx
import re
from typing import Optional
from ..lib.email_deduplicator import EmailDeduplicator
from ..lib.url_normalizer import URLNormalizer


class ReadmeParser:
    """
    Layer 3: Parse profile README for contact information.

    Extracts contact info from GitHub profile README (username/username repository).

    Constitutional Rules:
    - CR-001: Privacy-First - Filters noreply emails
    - CR-004: Transparency - Records source as 'readme'
    """

    def __init__(self, github_token: str):
        """
        Initialize README parser.

        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token
        self.deduplicator = EmailDeduplicator()
        self.url_normalizer = URLNormalizer()

        # Regex patterns
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.linkedin_pattern = re.compile(r"linkedin\.com/in/([^/\s\)\"\']+)", re.IGNORECASE)
        self.twitter_pattern = re.compile(r"(?:twitter\.com|x\.com)/([^/\s\)\"\']+)", re.IGNORECASE)
        # Twitter handle pattern with negative lookbehind to exclude email addresses
        self.twitter_handle_pattern = re.compile(r"(?<![A-Za-z0-9._%+-])@([A-Za-z0-9_]+)")
        self.url_pattern = re.compile(r"https?://([^\s\)\"\']+)")

    async def _fetch_github_readme(self, username: str) -> Optional[str]:
        """
        Fetch profile README content from GitHub API.

        Args:
            username: GitHub username

        Returns:
            README content as string or None if not found
        """
        # Try {username}/{username} repository first
        url = f"https://api.github.com/repos/{username}/{username}/readme"
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
                    data = response.json()
                    # README content is base64 encoded
                    content_b64 = data.get("content", "")
                    if content_b64:
                        # Decode base64
                        content_bytes = base64.b64decode(content_b64)
                        return content_bytes.decode("utf-8", errors="ignore")
                    return None
                elif response.status_code == 404:
                    # No README found
                    return None
                else:
                    # Other errors (rate limit, etc.)
                    return None
        except Exception:
            # Network errors, timeouts, decode errors, etc.
            return None

    async def parse(self, readme_content: Optional[str] = None, username: Optional[str] = None, fetch_fresh: bool = False) -> dict:
        """
        Parse README content for contact information.

        Args:
            readme_content: Raw README markdown content (optional)
            username: GitHub username (required if fetch_fresh=True)
            fetch_fresh: If True, fetch fresh README from GitHub API

        Returns:
            Dict with extracted contact fields and sources
        """
        # Fetch fresh data if requested
        if fetch_fresh and username:
            fresh_content = await self._fetch_github_readme(username)
            if fresh_content:
                readme_content = fresh_content

        if not readme_content:
            return {
                "emails": [],
                "linkedin_username": None,
                "twitter_username": None,
                "website": None,
                "contact_sources": {},
            }

        result = {
            "emails": [],
            "linkedin_username": None,
            "twitter_username": None,
            "website": None,
            "contact_sources": {},
        }

        # Extract emails
        email_matches = self.email_pattern.findall(readme_content)
        if email_matches:
            # Deduplicate and filter (noreply, spam, invalid)
            result["emails"] = self.deduplicator.deduplicate(email_matches)
            if result["emails"]:
                result["contact_sources"]["emails"] = "readme"

        # Extract LinkedIn username
        linkedin_match = self.linkedin_pattern.search(readme_content)
        if linkedin_match:
            username = linkedin_match.group(1)
            result["linkedin_username"] = username
            result["contact_sources"]["linkedin_username"] = "readme"

        # Extract Twitter username
        twitter_match = self.twitter_pattern.search(readme_content)
        if twitter_match:
            username = twitter_match.group(1)
            result["twitter_username"] = username
            result["contact_sources"]["twitter_username"] = "readme"
        elif not result["twitter_username"]:
            # Try finding @handle pattern
            handle_match = self.twitter_handle_pattern.search(readme_content)
            if handle_match:
                username = handle_match.group(1)
                result["twitter_username"] = username
                result["contact_sources"]["twitter_username"] = "readme"

        # Extract website/blog URL
        url_matches = self.url_pattern.findall(readme_content)
        if url_matches:
            # Take first non-social URL as website
            for url in url_matches:
                if not any(
                    domain in url.lower()
                    for domain in ["github.com", "linkedin.com", "twitter.com", "x.com"]
                ):
                    result["website"] = f"https://{url}"
                    break

        return result
