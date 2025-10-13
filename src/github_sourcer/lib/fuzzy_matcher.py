"""
FuzzyMatcher Library
====================
Fuzzy string matching using Levenshtein distance for typo tolerance.

Part of Module 002: GitHub Sourcer - Enhanced Location Matching
"""

import logging
from typing import Tuple
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Fuzzy string matching for handling typos and variants.

    Uses Levenshtein distance with configurable threshold.
    """

    def __init__(self, threshold: float = 0.8):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum similarity score (0.0-1.0) to consider a match
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

        self.threshold = threshold
        logger.debug(f"FuzzyMatcher initialized with threshold={threshold}")

    def fuzzy_match(
        self, str1: str, str2: str, threshold: float = None
    ) -> Tuple[bool, float]:
        """
        Perform fuzzy matching between two strings.

        Args:
            str1: First string
            str2: Second string
            threshold: Override default threshold for this match

        Returns:
            Tuple of (matched: bool, confidence: float)
            - matched: True if similarity >= threshold
            - confidence: Similarity score (0.0-1.0)

        Examples:
            >>> matcher = FuzzyMatcher(threshold=0.8)
            >>> matcher.fuzzy_match("Bangalore", "Bangalor")
            (True, 0.89)
            >>> matcher.fuzzy_match("Chennai", "Mumbai")
            (False, 0.25)
        """
        if not str1 or not str2:
            return (False, 0.0)

        # Use provided threshold or default
        match_threshold = threshold if threshold is not None else self.threshold

        # Normalize strings (case-insensitive, strip whitespace)
        normalized_str1 = str1.strip().lower()
        normalized_str2 = str2.strip().lower()

        # Exact match after normalization
        if normalized_str1 == normalized_str2:
            return (True, 1.0)

        # Calculate similarity using ratio (0-100 scale)
        similarity_score = fuzz.ratio(normalized_str1, normalized_str2) / 100.0

        # Check if match
        matched = similarity_score >= match_threshold

        logger.debug(
            f"Fuzzy match: '{str1}' vs '{str2}' = "
            f"{similarity_score:.2f} (threshold={match_threshold}, matched={matched})"
        )

        return (matched, similarity_score)

    def find_best_match(
        self, query: str, candidates: list[str], threshold: float = None
    ) -> Tuple[str | None, float]:
        """
        Find the best matching candidate from a list.

        Args:
            query: Query string to match
            candidates: List of candidate strings
            threshold: Override default threshold

        Returns:
            Tuple of (best_match: str | None, confidence: float)
            - best_match: Best matching candidate or None if no match above threshold
            - confidence: Similarity score of best match

        Examples:
            >>> matcher = FuzzyMatcher(threshold=0.8)
            >>> matcher.find_best_match("Bangalor", ["Bangalore", "Chennai", "Mumbai"])
            ("Bangalore", 0.89)
        """
        if not query or not candidates:
            return (None, 0.0)

        match_threshold = threshold if threshold is not None else self.threshold

        best_match = None
        best_score = 0.0

        for candidate in candidates:
            matched, score = self.fuzzy_match(query, candidate, threshold=match_threshold)

            if score > best_score:
                best_score = score
                best_match = candidate

        # Return None if no candidate meets threshold
        if best_score < match_threshold:
            return (None, best_score)

        logger.debug(
            f"Best match for '{query}': '{best_match}' with score {best_score:.2f}"
        )

        return (best_match, best_score)

    def get_similarity(self, str1: str, str2: str) -> float:
        """
        Get raw similarity score without threshold checking.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0.0-1.0)
        """
        _, confidence = self.fuzzy_match(str1, str2, threshold=0.0)
        return confidence
