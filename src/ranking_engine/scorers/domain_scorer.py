"""Domain relevance scoring using LLM."""

import json
import logging
from typing import Optional

from src.github_sourcer.models.candidate import Candidate
from src.jd_parser.llm_client import LLMClient, create_llm_client

logger = logging.getLogger(__name__)


class DomainScorer:
    """Calculates domain relevance score using LLM-based matching."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize domain scorer.

        Args:
            llm_client: LLM client for semantic matching (default: OpenAI GPT-4o-mini)
        """
        if llm_client is None:
            llm_client = create_llm_client("openai")
        self.llm_client = llm_client

        self.prompt_template = """You are a technical recruiter assessing domain relevance.

Job Domain: {job_domain}

Candidate's Repository Names and Descriptions:
{repos_info}

Task: Assess how many of the candidate's repositories are relevant to the job domain.
Consider project names, descriptions, and technologies used.

Return ONLY a JSON object:
{{
  "relevant_repo_count": <number>,
  "total_repo_count": <number>,
  "reasoning": "<brief explanation>"
}}

JSON Response:"""

    def score(
        self,
        candidate: Candidate,
        job_domain: Optional[str]
    ) -> tuple[float, str]:
        """
        Calculate domain relevance score.

        Args:
            candidate: Candidate with GitHub repos
            job_domain: Job domain from requirement (e.g., "fintech", "healthcare")

        Returns:
            Tuple of (score 0-100, reasoning string)
        """
        # If no domain specified, return 0
        if not job_domain:
            return (0.0, "No domain specified")

        # If candidate has no repos, return 0
        if not candidate.top_repos:
            return (0.0, "No repositories found")

        logger.debug(
            f"Scoring domain relevance: {len(candidate.top_repos)} repos against '{job_domain}'"
        )

        # Use LLM to assess domain relevance
        relevant_count, total_count, reasoning = self._assess_relevance(
            candidate.top_repos,
            job_domain
        )

        # Calculate score based on percentage of relevant repos
        if total_count == 0:
            score = 0.0
        else:
            percentage = (relevant_count / total_count) * 100
            score = min(100.0, percentage)

        logger.debug(
            f"Domain score: {score:.1f} ({relevant_count}/{total_count} relevant repos)"
        )

        return (score, reasoning)

    def _assess_relevance(
        self,
        repos: list,
        job_domain: str
    ) -> tuple[int, int, str]:
        """
        Use LLM to assess how many repos are relevant to job domain.

        Returns:
            Tuple of (relevant_count, total_count, reasoning)
        """
        # Build repos info string
        repos_info = "\n".join([
            f"- {repo.name}: {repo.description or 'No description'} (languages: {', '.join(repo.languages)})"
            for repo in repos[:10]  # Limit to first 10 repos
        ])

        # Build prompt
        prompt = self.prompt_template.format(
            job_domain=job_domain,
            repos_info=repos_info
        )

        try:
            # Get LLM response
            response = self.llm_client.complete(prompt, max_tokens=300, temperature=0.3)

            # Parse JSON
            result = json.loads(response)

            relevant_count = result.get("relevant_repo_count", 0)
            total_count = result.get("total_repo_count", len(repos))
            reasoning = result.get("reasoning", "Domain assessment completed")

            return (relevant_count, total_count, reasoning)

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            logger.error(f"Raw response: {response}")
            # Fallback: no relevant repos
            return (0, len(repos), "Failed to assess domain relevance")
        except Exception as e:
            logger.error(f"Domain scoring error: {e}")
            # Fallback: no relevant repos
            return (0, len(repos), "Failed to assess domain relevance")
