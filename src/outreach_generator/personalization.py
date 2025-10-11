"""Personalization engine for selecting relevant repos and determining depth."""

import logging
from typing import Optional

from src.github_sourcer.models.candidate import Candidate
from src.jd_parser.models import JobRequirement

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """Engine for analyzing candidates and selecting personalization strategies."""

    def select_relevant_repos(
        self,
        candidate: Candidate,
        job_requirement: JobRequirement
    ) -> list[dict]:
        """
        Select top 2-3 most relevant repositories for personalization.

        Scores repos based on:
        - Language match with required skills
        - Domain relevance (if specified)
        - Popularity (stars as tie-breaker)

        Args:
            candidate: Candidate from Module 002
            job_requirement: Job requirements from Module 001

        Returns:
            List of dicts with repo info: name, description, stars, relevance_score
            Empty list if candidate has no repos
        """
        if not candidate.top_repos:
            logger.info(f"Candidate {candidate.github_username} has no repos")
            return []

        # Extract job context
        required_skills = [s.lower() for s in job_requirement.required_skills]
        domain = job_requirement.domain.lower() if job_requirement.domain else None

        # Score each repo
        scored_repos = []
        for repo in candidate.top_repos:
            score = self._score_repo(repo, required_skills, domain)
            scored_repos.append({
                "name": repo.name,
                "description": repo.description or "",
                "stars": repo.stars,
                "languages": repo.languages or [],
                "relevance_score": score
            })

        # Sort by relevance score desc, then stars desc
        scored_repos.sort(key=lambda r: (r["relevance_score"], r["stars"]), reverse=True)

        # Return top 3
        top_repos = scored_repos[:3]
        logger.info(
            f"Selected {len(top_repos)} repos for {candidate.github_username}: "
            f"{[r['name'] for r in top_repos]}"
        )

        return top_repos

    def _score_repo(
        self,
        repo,
        required_skills: list[str],
        domain: Optional[str]
    ) -> float:
        """
        Score a single repository for relevance.

        Args:
            repo: Repository object from Candidate
            required_skills: Lowercase list of required skills
            domain: Lowercase domain string or None

        Returns:
            Relevance score (higher is better)
        """
        score = 0.0

        # Language match with required skills (primary signal)
        # Repository.languages is a list, not a single string
        repo_langs = [lang.lower() for lang in repo.languages] if repo.languages else []
        for skill in required_skills:
            for lang in repo_langs:
                if skill in lang or lang in skill:
                    score += 10.0
                    break  # Count each skill match only once

        # Check repo name/description for skill mentions
        repo_text = f"{repo.name} {repo.description or ''}".lower()
        for skill in required_skills:
            if skill in repo_text:
                score += 5.0

        # Domain relevance (if specified)
        if domain:
            if domain in repo_text:
                score += 8.0

        # Popularity boost (stars contribute minimally)
        # Normalize stars: 0-100 stars = 0-1 point, 100-1000 = 1-2 points, etc.
        if repo.stars > 0:
            score += min(3.0, (repo.stars / 100.0))

        return score

    def determine_personalization_depth(self, rank: int) -> str:
        """
        Determine personalization depth based on candidate rank.

        Args:
            rank: Candidate ranking position (1-indexed)

        Returns:
            Depth level: "deep", "medium", or "surface"
        """
        if rank <= 5:
            return "deep"
        elif rank <= 15:
            return "medium"
        else:
            return "surface"
