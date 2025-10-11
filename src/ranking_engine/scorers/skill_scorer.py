"""Skill match scoring for ranking engine."""

import logging

logger = logging.getLogger(__name__)


class SkillScorer:
    """Calculates skill match score based on percentage of required skills matched."""

    def score(
        self,
        matched_skills: list[str],
        required_skills: list[str]
    ) -> float:
        """
        Calculate skill match score as percentage.

        Args:
            matched_skills: List of required skills found in candidate profile
            required_skills: List of all required skills from job

        Returns:
            Score from 0-100 (percentage of required skills matched)

        Examples:
            - 0 of 5 matched → 0.0
            - 3 of 5 matched → 60.0
            - 5 of 5 matched → 100.0
            - Empty required_skills → 100.0 (no requirements = perfect match)
        """
        # Edge case: no required skills means perfect match
        if not required_skills:
            logger.debug("No required skills - returning perfect score")
            return 100.0

        # Calculate percentage
        matched_count = len(matched_skills)
        required_count = len(required_skills)

        percentage = (matched_count / required_count) * 100

        logger.debug(
            f"Skill match: {matched_count}/{required_count} = {percentage:.1f}%"
        )

        return percentage
