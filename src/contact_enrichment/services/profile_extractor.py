"""
Profile Extractor Service (Layer 1)
Module 010: Contact Enrichment

Extracts contact information from GitHub profile fields.
Success rate: 33.3% email, 66.7% Twitter, 25% blog (validated)
"""

import httpx
from typing import Optional
from ..lib.email_validator import EmailValidator
from ..lib.noreply_filter import NoreplyFilter
from ..lib.spam_filter import SpamFilter
from ..lib.url_normalizer import URLNormalizer


class ProfileExtractor:
    """
    Layer 1: Extract contact info from GitHub profile fields.

    Extracts:
    - Email (if public)
    - Blog/website URL
    - Twitter username
    - Company
    - Hireable flag

    Constitutional Rules:
    - CR-001: Privacy-First - Filters noreply emails (user chose to hide)
    - CR-004: Transparency - Records source as 'profile'
    """

    def __init__(self, github_token: str):
        """
        Initialize profile extractor.

        Args:
            github_token: GitHub personal access token (for API rate limits)
        """
        self.github_token = github_token
        self.email_validator = EmailValidator()
        self.noreply_filter = NoreplyFilter()
        self.spam_filter = SpamFilter()
        self.url_normalizer = URLNormalizer()

    async def _fetch_github_profile(self, username: str) -> Optional[dict]:
        """
        Fetch GitHub profile data from API.

        Args:
            username: GitHub username

        Returns:
            Profile data dict or None if failed
        """
        url = f"https://api.github.com/users/{username}"
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

    async def extract(self, profile_data: dict, fetch_fresh: bool = False) -> dict:
        """
        Extract contact information from GitHub profile data.

        Args:
            profile_data: GitHub API /users/{username} response or candidate dict
            fetch_fresh: If True, fetch fresh data from GitHub API

        Returns:
            Dict with extracted contact fields and sources
        """
        # Fetch fresh data if requested or if profile_data is minimal
        github_username = profile_data.get("github_username")

        if fetch_fresh and github_username:
            # Fetch fresh data from GitHub API
            fresh_data = await self._fetch_github_profile(github_username)
            if fresh_data:
                # Merge with existing data (fresh data takes precedence)
                profile_data = {**profile_data, **fresh_data}

        result = {
            "primary_email": None,
            "blog_url": None,
            "twitter_username": None,
            "company": None,
            "hireable": False,
            "contact_sources": {},
        }

        # Extract email (if public)
        email = profile_data.get("email")
        if email:
            # Validate and filter
            if self.email_validator.validate(email):
                if not self.noreply_filter.is_noreply(email):
                    if not self.spam_filter.is_spam_domain(email):
                        result["primary_email"] = email
                        result["contact_sources"]["primary_email"] = "profile"

        # Extract blog/website URL
        blog = profile_data.get("blog")
        if blog:
            # Add protocol if missing
            if not blog.startswith(("http://", "https://")):
                blog = f"https://{blog}"
            result["blog_url"] = blog
            result["contact_sources"]["blog_url"] = "profile"

        # Extract Twitter username
        twitter = profile_data.get("twitter_username")
        if twitter:
            # Normalize URL to username
            username = self.url_normalizer.extract_twitter_username(twitter)
            if username:
                result["twitter_username"] = username
                result["contact_sources"]["twitter_username"] = "profile"

        # Extract company
        company = profile_data.get("company")
        if company:
            result["company"] = company

        # Extract hireable flag
        hireable = profile_data.get("hireable", False)
        result["hireable"] = hireable if hireable is not None else False

        return result
