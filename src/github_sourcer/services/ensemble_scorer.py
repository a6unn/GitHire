"""
EnsembleScorer Service
======================
Combine multiple scoring signals to rank candidates effectively.

Part of Module 002: GitHub Sourcer - Enhanced Ensemble Scoring
"""

import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone
from src.github_sourcer.models.candidate_score import CandidateScore
from src.github_sourcer.models.skill_confidence import SkillConfidence
from src.github_sourcer.models.location_hierarchy import LocationHierarchy

logger = logging.getLogger(__name__)


class EnsembleScorer:
    """
    Ensemble scoring for candidate ranking.

    Combines multiple signals with configurable weights:
    - Skill matching (0.5 weight)
    - Location matching (0.3 weight)
    - Activity/recency (0.2 weight)
    """

    # Ensemble weights (must sum to 1.0)
    ENSEMBLE_WEIGHTS = {
        'skill_match': 0.5,
        'location_match': 0.3,
        'activity': 0.2
    }

    def __init__(self):
        """Initialize EnsembleScorer."""
        # Verify weights sum to 1.0
        total_weight = sum(self.ENSEMBLE_WEIGHTS.values())
        if abs(total_weight - 1.0) > 0.001:
            logger.warning(f"Ensemble weights do not sum to 1.0: {total_weight}")

    def score_candidate(
        self,
        candidate: Dict,
        skills: List[SkillConfidence],
        location_match: Optional[Tuple[LocationHierarchy, str, float]] = None,
        search_location: Optional[LocationHierarchy] = None,
        required_skills: Optional[List[str]] = None
    ) -> CandidateScore:
        """
        Score a single candidate using ensemble scoring.

        Args:
            candidate: Candidate dict with username and profile data
            skills: List of SkillConfidence objects
            location_match: Tuple of (candidate_location, match_level, confidence)
            search_location: Search location hierarchy
            required_skills: List of required skill names (optional)

        Returns:
            CandidateScore with total_score and signal breakdown

        Examples:
            >>> scorer = EnsembleScorer()
            >>> candidate = {"username": "johndoe", "profile": {"public_repos": 50}}
            >>> skills = [SkillConfidence(...)]
            >>> score = scorer.score_candidate(candidate, skills, required_skills=["Python"])
            >>> score.total_score
            0.75
        """
        username = candidate.get("username", "unknown")
        profile = candidate.get("profile", {})

        # Calculate individual signal scores
        skill_match_score = self._calculate_skill_match_score(skills, required_skills)
        location_match_score = self._calculate_location_match_score(location_match)
        activity_score = self._calculate_activity_score(profile)

        # Calculate weighted contributions
        skill_contribution = skill_match_score * self.ENSEMBLE_WEIGHTS['skill_match']
        location_contribution = location_match_score * self.ENSEMBLE_WEIGHTS['location_match']
        activity_contribution = activity_score * self.ENSEMBLE_WEIGHTS['activity']

        # Total score
        total_score = skill_contribution + location_contribution + activity_contribution

        # Build signal contributions dict
        signal_contributions = {
            'skill_match': skill_contribution,
            'location_match': location_contribution,
            'activity': activity_contribution
        }

        return CandidateScore(
            username=username,
            total_score=total_score,
            skill_match_score=skill_match_score,
            location_match_score=location_match_score,
            activity_score=activity_score,
            signal_contributions=signal_contributions
        )

    def rank_candidates(
        self,
        candidates_data: List[Tuple[Dict, List[SkillConfidence], Optional[Tuple]]],
        required_skills: Optional[List[str]] = None,
        search_location: Optional[LocationHierarchy] = None,
        min_score: float = 0.0
    ) -> List[CandidateScore]:
        """
        Rank multiple candidates by ensemble score.

        Args:
            candidates_data: List of (candidate, skills, location_match) tuples
            required_skills: List of required skill names
            search_location: Search location hierarchy
            min_score: Minimum score threshold (default: 0.0)

        Returns:
            List of CandidateScore objects sorted by total_score (descending)

        Examples:
            >>> scorer = EnsembleScorer()
            >>> candidates_data = [(candidate1, skills1, location1), ...]
            >>> ranked = scorer.rank_candidates(candidates_data, required_skills=["Python"])
            >>> ranked[0].username
            'top_candidate'
        """
        scored_candidates = []

        for candidate, skills, location_match in candidates_data:
            score = self.score_candidate(
                candidate=candidate,
                skills=skills,
                location_match=location_match,
                search_location=search_location,
                required_skills=required_skills
            )

            # Apply minimum score threshold
            if score.total_score >= min_score:
                scored_candidates.append(score)

        # Sort by total_score (descending)
        scored_candidates.sort(key=lambda s: s.total_score, reverse=True)

        logger.info(
            f"Ranked {len(scored_candidates)} candidates "
            f"(filtered from {len(candidates_data)} with min_score={min_score})"
        )

        return scored_candidates

    def _calculate_skill_match_score(
        self,
        skills: List[SkillConfidence],
        required_skills: Optional[List[str]] = None
    ) -> float:
        """
        Calculate skill matching score.

        If required_skills specified:
          - Score based on overlap with required skills
          - Weighted by confidence scores

        If no required_skills:
          - Use average confidence of all skills

        Returns:
            Score between 0.0 and 1.0
        """
        if not skills:
            return 0.0

        if not required_skills:
            # No required skills - use average confidence of all detected skills
            total_confidence = sum(s.confidence_score for s in skills)
            return total_confidence / len(skills)

        # Calculate overlap with required skills
        skill_names = {s.skill_name.lower(): s for s in skills}
        required_lower = [s.lower() for s in required_skills]

        matched_skills = []
        for req_skill in required_lower:
            if req_skill in skill_names:
                matched_skills.append(skill_names[req_skill])

        if not matched_skills:
            return 0.0

        # Score = (matched_count / required_count) * avg_confidence
        match_ratio = len(matched_skills) / len(required_skills)
        avg_confidence = sum(s.confidence_score for s in matched_skills) / len(matched_skills)

        score = match_ratio * avg_confidence

        return min(score, 1.0)

    def _calculate_location_match_score(
        self,
        location_match: Optional[Tuple[LocationHierarchy, str, float]] = None
    ) -> float:
        """
        Calculate location matching score.

        Uses hierarchical confidence from LocationParser:
        - City match: 1.0
        - State match: 0.7
        - Country match: 0.3

        Returns:
            Score between 0.0 and 1.0
        """
        if not location_match:
            return 0.0

        candidate_location, match_level, confidence = location_match

        # Return confidence directly (already weighted by LocationParser)
        return confidence

    def _calculate_activity_score(self, profile: Dict) -> float:
        """
        Calculate activity/recency score.

        Components:
        - Public repos (0-1 normalized, capped at 100 repos = 1.0)
        - Followers (0-1 normalized, capped at 1000 followers = 1.0)
        - Account recency (0-1 based on account age, newer = higher)

        Returns:
            Score between 0.0 and 1.0
        """
        if not profile:
            return 0.0

        # Repos score (cap at 100 repos)
        public_repos = profile.get('public_repos', 0)
        repos_score = min(public_repos / 100.0, 1.0)

        # Followers score (cap at 1000 followers)
        followers = profile.get('followers', 0)
        followers_score = min(followers / 1000.0, 1.0)

        # Recency score (newer accounts = higher score)
        recency_score = self._calculate_recency_score(profile.get('created_at'))

        # Weighted average
        # Repos: 50%, Followers: 30%, Recency: 20%
        activity_score = (
            repos_score * 0.5 +
            followers_score * 0.3 +
            recency_score * 0.2
        )

        return min(activity_score, 1.0)

    def _calculate_recency_score(self, created_at: Optional[str]) -> float:
        """
        Calculate recency score based on account age.

        - Accounts < 1 year old: 1.0
        - Accounts 1-5 years old: 0.8-1.0 (linear decay)
        - Accounts > 5 years old: 0.5-0.8 (slower decay)

        Returns:
            Score between 0.0 and 1.0
        """
        if not created_at:
            return 0.5  # Default neutral score

        try:
            # Parse ISO 8601 timestamp - GitHub returns format like "2015-03-15T12:00:00Z"
            # Remove 'Z' and add timezone explicitly
            if created_at.endswith('Z'):
                created_at = created_at[:-1] + '+00:00'

            created_date = datetime.fromisoformat(created_at)

            # Ensure created_date is timezone-aware
            if created_date.tzinfo is None:
                created_date = created_date.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)

            # Calculate age in years
            age_days = (now - created_date).days
            age_years = age_days / 365.25

            if age_years < 1:
                return 1.0
            elif age_years < 5:
                # Linear decay from 1.0 to 0.8
                return 1.0 - (age_years - 1) * 0.05
            else:
                # Slower decay from 0.8 to 0.5
                return max(0.8 - (age_years - 5) * 0.02, 0.5)

        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse created_at '{created_at}': {e}")
            return 0.5  # Default neutral score
