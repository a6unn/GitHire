"""
URL Normalizer Library
Module 010: Contact Enrichment

Extracts clean usernames from social media URLs.
"""

from typing import Optional
import re
from urllib.parse import urlparse


class URLNormalizer:
    """
    Normalizes social media URLs to extract clean usernames.

    Supports:
    - LinkedIn: https://linkedin.com/in/username -> username
    - Twitter: https://twitter.com/username -> username
    - X.com: https://x.com/username -> username
    - Handles: @username -> username
    """

    def extract_linkedin_username(self, value: Optional[str]) -> Optional[str]:
        """
        Extract LinkedIn username from URL or return as-is.

        Args:
            value: LinkedIn URL or username

        Returns:
            Clean username or None
        """
        if not value:
            return None

        # If it's already a plain username (no slash), return as-is
        if "/" not in value:
            return value

        # Parse URL and extract username
        # Pattern: linkedin.com/in/username
        match = re.search(r"linkedin\.com/in/([^/?#]+)", value, re.IGNORECASE)
        if match:
            return match.group(1)

        # Fallback: return as-is if no pattern matched
        return value

    def extract_twitter_username(self, value: Optional[str]) -> Optional[str]:
        """
        Extract Twitter/X username from URL or handle.

        Args:
            value: Twitter URL, handle (@username), or username

        Returns:
            Clean username (without @) or None
        """
        if not value:
            return None

        # Remove @ prefix if present
        if value.startswith("@"):
            return value[1:]

        # If it's already a plain username (no slash, no @), return as-is
        if "/" not in value:
            return value

        # Parse URL and extract username
        # Pattern: twitter.com/username or x.com/username
        match = re.search(
            r"(?:twitter\.com|x\.com)/([^/?#]+)", value, re.IGNORECASE
        )
        if match:
            return match.group(1)

        # Fallback: return as-is if no pattern matched
        return value
