"""Main ranker class that orchestrates all scoring components."""

import logging
from typing import Optional

from src.github_sourcer.models.candidate import Candidate
from src.jd_parser.models import JobRequirement
from src.jd_parser.llm_client import LLMClient

from .models import RankedCandidate, ScoreWeights, ScoreBreakdown
from .skill_matcher import SkillMatcher
from .scorers.skill_scorer import SkillScorer
from .scorers.experience_scorer import ExperienceScorer
from .scorers.activity_scorer import ActivityScorer
from .scorers.domain_scorer import DomainScorer

logger = logging.getLogger(__name__)


class Ranker:
    """Main ranking engine that scores and ranks candidates."""

    def __init__(
        self,
        weights: Optional[ScoreWeights] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize ranker with scoring components.

        Args:
            weights: Score weights (default: 40% skills, 20% each for experience/activity/domain)
            llm_client: LLM client for semantic matching
        """
        self.weights = weights or ScoreWeights()

        # Initialize all scorers
        self.skill_matcher = SkillMatcher(llm_client)
        self.skill_scorer = SkillScorer()
        self.experience_scorer = ExperienceScorer()
        self.activity_scorer = ActivityScorer()
        self.domain_scorer = DomainScorer(llm_client)

        logger.info(f"Ranker initialized with weights: {self.weights}")

    def rank(
        self,
        candidates: list[Candidate],
        job_requirement: JobRequirement
    ) -> list[RankedCandidate]:
        """
        Score and rank all candidates.

        Args:
            candidates: List of candidates from GitHub Sourcer
            job_requirement: Job requirements from JD Parser

        Returns:
            List of RankedCandidate objects sorted by total_score (highest first)
        """
        if not candidates:
            logger.info("No candidates to rank")
            return []

        logger.info(f"Ranking {len(candidates)} candidates")

        # Adjust weights if domain not specified
        weights = self._adjust_weights_for_domain(job_requirement.domain)

        # Score all candidates
        ranked_candidates = []
        for candidate in candidates:
            ranked = self._score_candidate(candidate, job_requirement, weights)
            ranked_candidates.append(ranked)

        # Sort by total_score descending, then by followers (tie-breaker)
        ranked_candidates.sort(
            key=lambda rc: (rc.total_score, rc.candidate.followers),
            reverse=True
        )

        # Assign ranks (1-indexed) by creating new objects
        final_ranked = []
        for idx, ranked in enumerate(ranked_candidates, start=1):
            # Create a new RankedCandidate with the correct rank
            final_rc = RankedCandidate(
                candidate=ranked.candidate,
                rank=idx,
                total_score=ranked.total_score,
                skill_match_score=ranked.skill_match_score,
                activity_score=ranked.activity_score,
                experience_score=ranked.experience_score,
                domain_score=ranked.domain_score,
                score_breakdown=ranked.score_breakdown
            )
            final_ranked.append(final_rc)

        logger.info(
            f"Ranking complete: top score = {final_ranked[0].total_score:.1f}, "
            f"lowest score = {final_ranked[-1].total_score:.1f}"
        )

        return final_ranked

    def _score_candidate(
        self,
        candidate: Candidate,
        job_requirement: JobRequirement,
        weights: ScoreWeights
    ) -> RankedCandidate:
        """Score a single candidate across all dimensions."""
        # Skill matching
        matched_skills, missing_skills = self.skill_matcher.match_skills(
            job_requirement.required_skills,
            candidate.languages
        )
        skill_score = self.skill_scorer.score(matched_skills, job_requirement.required_skills)

        # Experience scoring
        experience_score, exp_reasoning = self.experience_scorer.score(candidate)

        # Activity scoring
        activity_score, activity_reasoning = self.activity_scorer.score(candidate)

        # Domain scoring
        domain_score, domain_reasoning = self.domain_scorer.score(
            candidate,
            job_requirement.domain
        )

        # Calculate weighted total
        total_score = (
            skill_score * weights.skill_match_weight +
            experience_score * weights.experience_weight +
            activity_score * weights.activity_weight +
            domain_score * weights.domain_weight
        )

        # Build score breakdown
        breakdown = ScoreBreakdown(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            activity_reasoning=activity_reasoning,
            experience_reasoning=exp_reasoning,
            domain_reasoning=domain_reasoning
        )

        # Create RankedCandidate
        ranked = RankedCandidate(
            candidate=candidate,
            rank=1,  # Temporary - will be reassigned after sorting
            total_score=total_score,
            skill_match_score=skill_score,
            activity_score=activity_score,
            experience_score=experience_score,
            domain_score=domain_score,
            score_breakdown=breakdown
        )

        logger.debug(
            f"Scored {candidate.github_username}: total={total_score:.1f} "
            f"(skill={skill_score:.1f}, exp={experience_score:.1f}, "
            f"activity={activity_score:.1f}, domain={domain_score:.1f})"
        )

        return ranked

    def _adjust_weights_for_domain(self, domain: Optional[str]) -> ScoreWeights:
        """
        Adjust weights when domain is not specified.

        Redistributes domain weight to other scores:
        - Skills: 50% (from 40%)
        - Experience: 25% (from 20%)
        - Activity: 25% (from 20%)
        - Domain: 0% (from 20%)
        """
        if domain:
            # Use default weights
            return self.weights

        logger.debug("No domain specified - redistributing weights")

        # Redistribute domain weight
        return ScoreWeights(
            skill_match_weight=0.50,
            experience_weight=0.25,
            activity_weight=0.25,
            domain_weight=0.00
        )
