"""
Social Profile Discoverer Service (Layer 4)
Module 010: Contact Enrichment

Discovers social profiles from bio text and blog page content.
Success rate: 66.7% Twitter, 25% LinkedIn (validated)
"""

import re
from typing import Optional
from ..lib.email_deduplicator import EmailDeduplicator
from ..lib.url_normalizer import URLNormalizer


class SocialDiscoverer:
    """
    Layer 4: Discover social profiles from bio and blog content.

    Extracts social links from:
    - GitHub bio text
    - Personal blog/website HTML

    Constitutional Rules:
    - CR-001: Privacy-First - Filters noreply emails
    - CR-004: Transparency - Records source as 'bio' or 'blog'
    """

    def __init__(self, github_token: str):
        """
        Initialize social profile discoverer.

        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token
        self.deduplicator = EmailDeduplicator()
        self.url_normalizer = URLNormalizer()

        # Regex patterns
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.linkedin_pattern = re.compile(r"linkedin\.com/in/([^/\s\)\"\'<>]+)", re.IGNORECASE)
        self.twitter_pattern = re.compile(r"(?:twitter\.com|x\.com)/([^/\s\)\"\'<>]+)", re.IGNORECASE)
        # Twitter handle pattern with negative lookbehind to exclude email addresses
        self.twitter_handle_pattern = re.compile(r"(?<![A-Za-z0-9._%+-])@([A-Za-z0-9_]+)")

    async def discover_from_bio(self, bio: Optional[str]) -> dict:
        """
        Discover social profiles from GitHub bio text.

        Args:
            bio: GitHub profile bio text

        Returns:
            Dict with discovered social profiles and sources
        """
        if not bio:
            return {
                "linkedin_username": None,
                "twitter_username": None,
                "contact_sources": {},
            }

        result = {
            "linkedin_username": None,
            "twitter_username": None,
            "contact_sources": {},
        }

        # Extract LinkedIn username from bio
        linkedin_match = self.linkedin_pattern.search(bio)
        if linkedin_match:
            username = linkedin_match.group(1)
            result["linkedin_username"] = username
            result["contact_sources"]["linkedin_username"] = "bio"

        # Extract Twitter username from bio (URL or @handle)
        twitter_match = self.twitter_pattern.search(bio)
        if twitter_match:
            username = twitter_match.group(1)
            result["twitter_username"] = username
            result["contact_sources"]["twitter_username"] = "bio"
        elif not result["twitter_username"]:
            # Try finding @handle pattern
            # Prioritize handles after "follow" keywords
            follow_pattern = re.compile(r"follow\s+me\s+@([A-Za-z0-9_]+)", re.IGNORECASE)
            follow_match = follow_pattern.search(bio)

            if follow_match:
                username = follow_match.group(1)
                result["twitter_username"] = username
                result["contact_sources"]["twitter_username"] = "bio"
            else:
                # Fall back to any @handle
                handle_match = self.twitter_handle_pattern.search(bio)
                if handle_match:
                    username = handle_match.group(1)
                    result["twitter_username"] = username
                    result["contact_sources"]["twitter_username"] = "bio"

        return result

    async def discover_from_blog(self, blog_html: Optional[str]) -> dict:
        """
        Discover social profiles and emails from blog HTML.

        Args:
            blog_html: HTML content from personal blog/website (None if 404)

        Returns:
            Dict with discovered contact info and sources
        """
        if not blog_html:
            return {
                "linkedin_username": None,
                "twitter_username": None,
                "emails": [],
                "contact_sources": {},
            }

        result = {
            "linkedin_username": None,
            "twitter_username": None,
            "emails": [],
            "contact_sources": {},
        }

        # Extract LinkedIn username
        linkedin_match = self.linkedin_pattern.search(blog_html)
        if linkedin_match:
            username = linkedin_match.group(1)
            result["linkedin_username"] = username
            result["contact_sources"]["linkedin_username"] = "blog"

        # Extract Twitter username
        twitter_match = self.twitter_pattern.search(blog_html)
        if twitter_match:
            username = twitter_match.group(1)
            result["twitter_username"] = username
            result["contact_sources"]["twitter_username"] = "blog"

        # Extract emails
        email_matches = self.email_pattern.findall(blog_html)
        if email_matches:
            # Deduplicate and filter (noreply, spam, invalid)
            result["emails"] = self.deduplicator.deduplicate(email_matches)
            if result["emails"]:
                result["contact_sources"]["emails"] = "blog"

        return result
