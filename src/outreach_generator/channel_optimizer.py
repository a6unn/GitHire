"""
Channel Optimizer - Channel-specific validation and formatting

This module provides validation and formatting logic for different outreach channels:
- Email: 50-125 words, subject 36-50 chars
- LinkedIn: <400 chars, 3-4 sentences
- Twitter: <280 chars, 2-3 sentences
"""

import re
from typing import Optional
from .models import ChannelType


class ChannelOptimizer:
    """
    Validates and formats outreach messages for specific channels.

    Ensures messages meet channel-specific constraints:
    - Email: Professional structure with subject line
    - LinkedIn: Concise professional message
    - Twitter: Very brief, casual message
    """

    # ========================================================================
    # Email Validation and Formatting
    # ========================================================================

    def validate_email(self, subject: str, body: str) -> tuple[bool, list[str]]:
        """
        Validate email message constraints.

        Args:
            subject: Email subject line
            body: Email body text

        Returns:
            Tuple of (is_valid, error_messages)

        Constraints:
            - Subject: 36-50 characters
            - Body: 50-125 words

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> is_valid, errors = optimizer.validate_email("Great opportunity at TechCorp", "...")
            >>> print(is_valid)
            False
            >>> print(errors)
            ['Subject line must be 36-50 characters (got 28)']
        """
        errors = []

        # Validate subject line length
        subject_len = len(subject)
        if subject_len < 36 or subject_len > 50:
            errors.append(f"Subject line must be 36-50 characters (got {subject_len})")

        # Validate body word count
        word_count = len(body.split())
        if word_count < 50 or word_count > 125:
            errors.append(f"Email body must be 50-125 words (got {word_count})")

        return (len(errors) == 0, errors)

    def format_for_email(self, subject: str, body: str) -> dict:
        """
        Format and validate email message.

        Args:
            subject: Email subject line
            body: Email body text

        Returns:
            Dictionary with formatted email:
            {
                "subject_line": str,
                "message_text": str,
                "channel": "email",
                "is_valid": bool,
                "validation_errors": list[str]
            }

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> result = optimizer.format_for_email(
            ...     "Redis expertise needed for distributed systems role",
            ...     "Hi John, I noticed your redis-clone project..."
            ... )
            >>> result["is_valid"]
            True
        """
        is_valid, errors = self.validate_email(subject, body)

        return {
            "subject_line": subject,
            "message_text": body,
            "channel": ChannelType.EMAIL.value,
            "is_valid": is_valid,
            "validation_errors": errors
        }

    # ========================================================================
    # LinkedIn Validation and Formatting
    # ========================================================================

    def validate_linkedin(self, message: str) -> tuple[bool, list[str]]:
        """
        Validate LinkedIn message constraints.

        Args:
            message: LinkedIn message text

        Returns:
            Tuple of (is_valid, error_messages)

        Constraints:
            - Total length: <400 characters
            - Sentence count: 3-4 sentences (heuristic)

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> is_valid, errors = optimizer.validate_linkedin("Short message.")
            >>> print(is_valid)
            False
            >>> print(errors)
            ['LinkedIn message should have 3-4 sentences (got 1)']
        """
        errors = []

        # Validate total length
        char_count = len(message)
        if char_count >= 400:
            errors.append(f"LinkedIn message must be <400 characters (got {char_count})")

        # Validate sentence count (heuristic: count periods, exclamation, question marks)
        sentence_endings = message.count('.') + message.count('!') + message.count('?')
        if sentence_endings < 3 or sentence_endings > 4:
            errors.append(f"LinkedIn message should have 3-4 sentences (got {sentence_endings})")

        return (len(errors) == 0, errors)

    def format_for_linkedin(self, message: str) -> dict:
        """
        Format and validate LinkedIn message.

        Args:
            message: LinkedIn message text

        Returns:
            Dictionary with formatted message:
            {
                "message_text": str,
                "channel": "linkedin",
                "is_valid": bool,
                "validation_errors": list[str]
            }

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> result = optimizer.format_for_linkedin(
            ...     "Hi John! Saw your redis-clone. We need that expertise. $150k-$200k. Chat?"
            ... )
            >>> result["is_valid"]
            True
        """
        is_valid, errors = self.validate_linkedin(message)

        return {
            "message_text": message,
            "channel": ChannelType.LINKEDIN.value,
            "is_valid": is_valid,
            "validation_errors": errors
        }

    # ========================================================================
    # Twitter Validation and Formatting
    # ========================================================================

    def validate_twitter(self, message: str) -> tuple[bool, list[str]]:
        """
        Validate Twitter message constraints.

        Args:
            message: Twitter message text

        Returns:
            Tuple of (is_valid, error_messages)

        Constraints:
            - Total length: <280 characters
            - Sentence count: 2-3 sentences (heuristic)

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> is_valid, errors = optimizer.validate_twitter("Very long message..." * 30)
            >>> print(is_valid)
            False
            >>> print(errors)
            ['Twitter message must be <280 characters (got 540)']
        """
        errors = []

        # Validate total length
        char_count = len(message)
        if char_count >= 280:
            errors.append(f"Twitter message must be <280 characters (got {char_count})")

        # Validate sentence count (heuristic: count periods, exclamation, question marks)
        sentence_endings = message.count('.') + message.count('!') + message.count('?')
        if sentence_endings < 2 or sentence_endings > 3:
            errors.append(f"Twitter message should have 2-3 sentences (got {sentence_endings})")

        return (len(errors) == 0, errors)

    def format_for_twitter(self, message: str) -> dict:
        """
        Format and validate Twitter message.

        Args:
            message: Twitter message text

        Returns:
            Dictionary with formatted message:
            {
                "message_text": str,
                "channel": "twitter",
                "is_valid": bool,
                "validation_errors": list[str]
            }

        Example:
            >>> optimizer = ChannelOptimizer()
            >>> result = optimizer.format_for_twitter(
            ...     "Loved your redis-clone! We're hiring for distributed systems. $150k. Interested?"
            ... )
            >>> result["is_valid"]
            True
        """
        is_valid, errors = self.validate_twitter(message)

        return {
            "message_text": message,
            "channel": ChannelType.TWITTER.value,
            "is_valid": is_valid,
            "validation_errors": errors
        }
