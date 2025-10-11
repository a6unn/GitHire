"""Skill matching with LLM-based semantic matching for ranking engine."""

import json
import logging
from typing import Optional

from src.jd_parser.llm_client import LLMClient, create_llm_client

logger = logging.getLogger(__name__)


class SkillMatcher:
    """Matches required skills against candidate languages using exact and semantic matching."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize skill matcher.

        Args:
            llm_client: LLM client for semantic matching (default: OpenAI GPT-4o-mini)
        """
        if llm_client is None:
            llm_client = create_llm_client("openai")
        self.llm_client = llm_client

        # Prompt template for semantic skill matching
        self.prompt_template = """You are a technical recruiter matching job requirements to candidate skills.

Job Required Skills: {required_skills}
Candidate Languages/Skills: {candidate_languages}

Task: Determine which required skills are matched by the candidate's languages/skills.
Use semantic understanding (e.g., "React" matches "Frontend Development", "FastAPI" matches "Python web frameworks").

Return ONLY a JSON object with this exact format:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3"]
}}

Rules:
1. matched_skills: Required skills found in candidate profile (exact or semantic match)
2. missing_skills: Required skills NOT found in candidate profile
3. Be generous with matches - recognize related technologies
4. All required skills must appear in either matched_skills OR missing_skills

JSON Response:"""

    def match_skills(
        self,
        required_skills: list[str],
        candidate_languages: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Match required skills against candidate languages.

        Args:
            required_skills: List of skills required by job
            candidate_languages: List of languages/skills from candidate profile

        Returns:
            Tuple of (matched_skills, missing_skills)

        Raises:
            ValueError: If LLM fails to return valid response
        """
        if not required_skills:
            return ([], [])

        if not candidate_languages:
            return ([], required_skills.copy())

        logger.debug(
            f"Matching {len(required_skills)} required skills against "
            f"{len(candidate_languages)} candidate languages"
        )

        # Phase 1: Exact matches (case-insensitive)
        matched_exact, remaining = self._exact_matches(required_skills, candidate_languages)

        logger.debug(f"Exact matches: {matched_exact}, Remaining: {remaining}")

        # Phase 2: If all matched exactly, return early
        if not remaining:
            return (matched_exact, [])

        # Phase 3: LLM semantic matching for remaining skills
        matched_semantic, missing = self._semantic_matches(
            remaining,
            candidate_languages
        )

        logger.debug(f"Semantic matches: {matched_semantic}, Missing: {missing}")

        # Combine exact and semantic matches
        all_matched = matched_exact + matched_semantic

        return (all_matched, missing)

    def _exact_matches(
        self,
        required_skills: list[str],
        candidate_languages: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Find exact matches (case-insensitive) between required and candidate skills.

        Returns:
            Tuple of (matched_skills, remaining_required_skills)
        """
        # Normalize candidate languages to lowercase for comparison
        candidate_lower = [lang.lower().strip() for lang in candidate_languages]

        matched = []
        remaining = []

        for skill in required_skills:
            skill_lower = skill.lower().strip()
            if skill_lower in candidate_lower:
                matched.append(skill)
            else:
                remaining.append(skill)

        return (matched, remaining)

    def _semantic_matches(
        self,
        required_skills: list[str],
        candidate_languages: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Use LLM to find semantic matches for remaining skills.

        Returns:
            Tuple of (matched_skills, missing_skills)
        """
        if not required_skills:
            return ([], [])

        # Build prompt
        prompt = self.prompt_template.format(
            required_skills=", ".join(required_skills),
            candidate_languages=", ".join(candidate_languages)
        )

        try:
            # Get LLM response
            response = self.llm_client.complete(prompt, max_tokens=500, temperature=0.2)

            # Parse JSON
            result = json.loads(response)

            matched = result.get("matched_skills", [])
            missing = result.get("missing_skills", [])

            # Filter matched skills to only include skills from required_skills
            # (LLM sometimes hallucinates extra skills)
            required_set = set(required_skills)
            filtered_matched = [skill for skill in matched if skill in required_set]
            filtered_missing = [skill for skill in missing if skill in required_set]

            # Validate that all required skills are accounted for
            accounted_for = set(filtered_matched) | set(filtered_missing)

            if accounted_for != required_set:
                logger.warning(
                    f"LLM response doesn't match required skills. "
                    f"Expected: {required_set}, Got: {set(matched) | set(missing)} (filtered to {accounted_for})"
                )
                # Fallback: mark unaccounted skills as missing
                for skill in required_skills:
                    if skill not in accounted_for:
                        filtered_missing.append(skill)

            return (filtered_matched, filtered_missing)

        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}")
            logger.error(f"Raw response: {response}")
            # Fallback: mark all as missing
            return ([], required_skills.copy())
        except Exception as e:
            logger.error(f"Semantic matching error: {e}")
            # Fallback: mark all as missing
            return ([], required_skills.copy())
