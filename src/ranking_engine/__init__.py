"""Ranking Engine Module (Module 003).

Scores and ranks GitHub candidates based on job requirements.
"""

from typing import Optional
from src.github_sourcer.models.candidate import Candidate
from src.jd_parser.models import JobRequirement

from .models import RankedCandidate, ScoreWeights, ScoreBreakdown
from .ranker import Ranker

__version__ = "0.1.0"


def rank_candidates(
    candidates: list[Candidate],
    job_requirement: JobRequirement,
    weights: Optional[ScoreWeights] = None
) -> list[RankedCandidate]:
    """
    Rank candidates based on job requirements.

    Convenience function that creates a Ranker and performs ranking.

    Args:
        candidates: List of candidates from Module 002 (GitHub Sourcer)
        job_requirement: Job requirements from Module 001 (JD Parser)
        weights: Optional custom score weights (default: 40% skills, 20% each other)

    Returns:
        List of RankedCandidate objects sorted by total_score (highest first)

    Example:
        ```python
        from src.jd_parser import parse_jd
        from src.github_sourcer import search_github
        from src.ranking_engine import rank_candidates

        # Parse JD
        job_req = parse_jd("Senior Python developer with 5 years experience...")

        # Search GitHub
        result = await search_github(job_req)

        # Rank candidates
        ranked = rank_candidates(result["candidates"], job_req)

        print(f"Top candidate: {ranked[0].github_username} (score: {ranked[0].total_score:.1f})")
        ```
    """
    ranker = Ranker(weights=weights)
    return ranker.rank(candidates, job_requirement)


__all__ = [
    "rank_candidates",
    "Ranker",
    "RankedCandidate",
    "ScoreWeights",
    "ScoreBreakdown",
]
