"""
Email Deduplicator Library
Module 010: Contact Enrichment

Deduplicates and prioritizes emails based on source quality.
"""

from typing import Optional
from .email_validator import EmailValidator
from .noreply_filter import NoreplyFilter
from .spam_filter import SpamFilter


class EmailDeduplicator:
    """
    Deduplicates emails and prioritizes by source quality.

    Features:
    - Case-insensitive deduplication
    - Filters noreply emails during deduplication
    - Filters spam/test domains during deduplication
    - Filters invalid email formats
    - Prioritizes emails by source quality (commit > profile > readme > bio)
    """

    # Source quality ranking (higher = better)
    SOURCE_PRIORITY = {"commit": 4, "profile": 3, "readme": 2, "bio": 1, "blog": 1}

    def __init__(self):
        """Initialize the deduplicator with required filters."""
        self.validator = EmailValidator()
        self.noreply_filter = NoreplyFilter()
        self.spam_filter = SpamFilter()

    def deduplicate(self, emails: list[str]) -> list[str]:
        """
        Deduplicate and filter emails.

        Args:
            emails: List of emails to deduplicate

        Returns:
            Deduplicated, filtered list of valid emails
        """
        if not emails:
            return []

        seen: set[str] = set()
        result: list[str] = []

        for email in emails:
            # Skip None/empty
            if not email:
                continue

            # Normalize to lowercase for comparison
            email_lower = email.lower()

            # Skip if already seen (case-insensitive)
            if email_lower in seen:
                continue

            # Filter invalid emails
            if not self.validator.validate(email):
                continue

            # Filter noreply emails
            if self.noreply_filter.is_noreply(email):
                continue

            # Filter spam domains
            if self.spam_filter.is_spam_domain(email):
                continue

            # Add to results (preserving original case of first occurrence)
            seen.add(email_lower)
            result.append(email)

        return result

    def prioritize(
        self, emails_with_sources: list[tuple[str, str]]
    ) -> Optional[str]:
        """
        Select the best email based on source quality.

        Args:
            emails_with_sources: List of (email, source) tuples

        Returns:
            Best quality email or None
        """
        if not emails_with_sources:
            return None

        # Filter to only valid emails
        valid_emails = []
        for email, source in emails_with_sources:
            if not email:
                continue

            # Validate and filter
            if not self.validator.validate(email):
                continue
            if self.noreply_filter.is_noreply(email):
                continue
            if self.spam_filter.is_spam_domain(email):
                continue

            valid_emails.append((email, source))

        if not valid_emails:
            return None

        # Sort by source priority (highest first)
        valid_emails.sort(
            key=lambda x: self.SOURCE_PRIORITY.get(x[1], 0), reverse=True
        )

        # Return best email
        return valid_emails[0][0]
