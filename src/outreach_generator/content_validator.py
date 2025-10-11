"""Content validation for generated outreach messages."""

import logging
import re
from typing import Optional

from src.github_sourcer.models.candidate import Candidate

logger = logging.getLogger(__name__)


class ContentValidator:
    """Validates generated outreach messages for quality and safety."""

    # Basic offensive keywords (simplified list for POC)
    OFFENSIVE_KEYWORDS = [
        "stupid", "idiot", "dumb", "fool", "sucks", "crap",
        "incompetent", "worthless", "pathetic"
    ]

    # Call-to-action keywords
    CTA_KEYWORDS = [
        "reach out", "connect", "discuss", "chat", "talk", "reply",
        "response", "interview", "call", "meeting", "schedule", "interested"
    ]

    def validate(
        self,
        message: str,
        candidate: Candidate
    ) -> tuple[bool, list[str]]:
        """
        Validate generated message for quality and safety.

        Args:
            message: Generated message text
            candidate: Candidate profile for cross-checking

        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True if message passes all checks
            - error_messages: List of validation errors (empty if valid)
        """
        errors = []

        # Safety checks
        errors.extend(self._check_length(message))
        errors.extend(self._check_offensive_content(message))

        # Quality checks
        errors.extend(self._check_mentions_candidate(message, candidate))
        errors.extend(self._check_has_cta(message))

        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Message validation failed: {errors}")

        return (is_valid, errors)

    def _check_length(self, message: str) -> list[str]:
        """Check message length is reasonable (50-1000 words)."""
        word_count = len(message.split())

        if word_count < 50:
            return ["Message too short (< 50 words)"]
        elif word_count > 1000:
            return ["Message too long (> 1000 words)"]

        return []

    def _check_offensive_content(self, message: str) -> list[str]:
        """Check for offensive or unprofessional language."""
        message_lower = message.lower()

        for keyword in self.OFFENSIVE_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                return [f"Message contains offensive language: '{keyword}'"]

        return []

    def _check_mentions_candidate(
        self,
        message: str,
        candidate: Candidate
    ) -> list[str]:
        """Check that message mentions candidate's name or username."""
        message_lower = message.lower()
        username_lower = candidate.github_username.lower()

        # Check for username
        if username_lower in message_lower:
            return []

        # Check for name (if available)
        if candidate.name:
            name_lower = candidate.name.lower()
            # Check first name or full name
            name_parts = name_lower.split()
            for part in name_parts:
                if len(part) > 2 and part in message_lower:  # Avoid matching initials
                    return []

        return ["Message does not mention candidate's name or username"]

    def _check_has_cta(self, message: str) -> list[str]:
        """Check that message includes a call-to-action."""
        message_lower = message.lower()

        for cta in self.CTA_KEYWORDS:
            if cta in message_lower:
                return []

        return ["Message does not include a clear call-to-action"]
