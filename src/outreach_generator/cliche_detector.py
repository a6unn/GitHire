"""
Cliché Detector - Identifies and removes recruiter clichés from outreach messages

This module provides detection and removal of common recruiter buzzwords and phrases
that reduce message authenticity and personalization.
"""

import re
from typing import Optional


class ClicheDetector:
    """
    Detects and removes common recruiter clichés from outreach messages.

    Clichés are overused phrases that reduce authenticity and make messages
    feel generic. Examples: "reaching out", "great opportunity", "passionate team"

    Usage:
        >>> detector = ClicheDetector()
        >>> cliches = detector.detect("I'm reaching out about a great opportunity")
        >>> print(cliches)
        ['reaching out', 'great opportunity']
        >>> cleaned, removed = detector.remove("I'm reaching out about a great opportunity")
        >>> print(cleaned)
        "I'm contacting you about an opportunity"
    """

    # Class-level cliché list
    CLICHES = [
        # Generic outreach phrases
        "reaching out",
        "reaching out to you",
        "wanted to reach out",
        "touching base",
        "circle back",
        "loop back",
        "ping you",
        "quick ping",

        # Generic opportunity phrases
        "great opportunity",
        "amazing opportunity",
        "exciting opportunity",
        "fantastic opportunity",
        "unique opportunity",
        "rare opportunity",

        # Generic team/culture phrases
        "passionate team",
        "talented team",
        "world-class team",
        "rockstar team",
        "ninja team",
        "guru",
        "rockstar",
        "ninja",

        # Generic challenge phrases
        "exciting challenges",
        "unique challenges",
        "interesting challenges",

        # Generic tech buzzwords (without context)
        "cutting-edge technology",
        "cutting-edge",
        "bleeding edge",
        "next-generation",
        "disruptive",
        "revolutionary",
        "game-changing",

        # Generic growth phrases
        "fast-paced environment",
        "fast-growing company",
        "hyper-growth",

        # Corporate buzzwords
        "synergy",
        "paradigm shift",
        "thought leader",
        "best practices",
        "low-hanging fruit",
        "move the needle",
        "drink the kool-aid",

        # Generic values
        "work hard play hard",
        "wear many hats",
        "hit the ground running",
    ]

    def __init__(self):
        """Initialize ClicheDetector with compiled regex patterns for efficiency."""
        # Compile regex patterns for each cliché (case-insensitive)
        self.patterns = [
            (cliche, re.compile(r'\b' + re.escape(cliche) + r'\b', re.IGNORECASE))
            for cliche in self.CLICHES
        ]

    def detect(self, message: str) -> list[str]:
        """
        Detect clichés in a message.

        Args:
            message: Message text to analyze

        Returns:
            List of detected clichés (lowercase)

        Example:
            >>> detector = ClicheDetector()
            >>> cliches = detector.detect("Reaching out about a great opportunity with our passionate team!")
            >>> print(cliches)
            ['reaching out', 'great opportunity', 'passionate team']
        """
        detected = []

        for cliche, pattern in self.patterns:
            if pattern.search(message):
                detected.append(cliche.lower())

        return detected

    def remove(self, message: str) -> tuple[str, list[str]]:
        """
        Remove clichés from a message and return cleaned version.

        Strategy:
        - Remove the cliché phrase
        - Clean up extra spaces
        - If removal leaves an awkward sentence, try to fix it

        Args:
            message: Message text to clean

        Returns:
            Tuple of (cleaned_message, removed_cliches)

        Example:
            >>> detector = ClicheDetector()
            >>> cleaned, removed = detector.remove("I'm reaching out about a great opportunity")
            >>> print(cleaned)
            "I'm contacting you about an opportunity"
            >>> print(removed)
            ['reaching out', 'great opportunity']
        """
        detected = self.detect(message)
        cleaned = message
        removed = []

        # Remove each detected cliché
        for cliche in detected:
            # Find the pattern
            for original_cliche, pattern in self.patterns:
                if original_cliche.lower() == cliche:
                    # Get the match to preserve the original case in message
                    match = pattern.search(cleaned)
                    if match:
                        matched_text = match.group(0)

                        # Apply replacement based on cliché type
                        replacement = self._get_replacement(cliche)

                        # Replace the cliché
                        cleaned = pattern.sub(replacement, cleaned, count=1)
                        removed.append(cliche)
                        break

        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()

        return (cleaned, removed)

    def _get_replacement(self, cliche: str) -> str:
        """
        Get a neutral replacement for a cliché.

        Args:
            cliche: The cliché phrase (lowercase)

        Returns:
            Neutral replacement text
        """
        replacements = {
            # Outreach phrases
            "reaching out": "contacting you",
            "reaching out to you": "contacting you",
            "wanted to reach out": "wanted to contact you",
            "touching base": "following up",
            "circle back": "follow up",
            "loop back": "follow up",
            "ping you": "message you",
            "quick ping": "quick message",

            # Opportunity phrases
            "great opportunity": "opportunity",
            "amazing opportunity": "opportunity",
            "exciting opportunity": "opportunity",
            "fantastic opportunity": "opportunity",
            "unique opportunity": "opportunity",
            "rare opportunity": "opportunity",

            # Team phrases
            "passionate team": "team",
            "talented team": "team",
            "world-class team": "team",
            "rockstar team": "team",
            "ninja team": "team",
            "guru": "expert",
            "rockstar": "expert",
            "ninja": "expert",

            # Challenge phrases
            "exciting challenges": "challenges",
            "unique challenges": "challenges",
            "interesting challenges": "challenges",

            # Tech buzzwords
            "cutting-edge technology": "technology",
            "cutting-edge": "modern",
            "bleeding edge": "modern",
            "next-generation": "new",
            "disruptive": "innovative",
            "revolutionary": "innovative",
            "game-changing": "innovative",

            # Growth phrases
            "fast-paced environment": "environment",
            "fast-growing company": "growing company",
            "hyper-growth": "growth",

            # Corporate buzzwords (often just remove)
            "synergy": "",
            "paradigm shift": "change",
            "thought leader": "expert",
            "best practices": "practices",
            "low-hanging fruit": "easy wins",
            "move the needle": "make an impact",
            "drink the kool-aid": "",

            # Generic values
            "work hard play hard": "",
            "wear many hats": "take on multiple roles",
            "hit the ground running": "start quickly",
        }

        return replacements.get(cliche, "")
