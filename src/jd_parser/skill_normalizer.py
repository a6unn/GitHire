"""Skill normalization with static lookup + LLM fallback."""

import json
from pathlib import Path
from typing import Optional


class SkillNormalizer:
    """Normalizes skill names using static mappings and LLM fallback."""

    def __init__(self, mappings_path: Optional[Path] = None, llm_client=None):
        """
        Initialize skill normalizer.

        Args:
            mappings_path: Path to skill_mappings.json (default: src/config/skill_mappings.json)
            llm_client: Optional LLM client for fallback normalization
        """
        if mappings_path is None:
            mappings_path = Path(__file__).parent.parent / "config" / "skill_mappings.json"

        with open(mappings_path) as f:
            data = json.load(f)
            self.mappings = data["mappings"]

        self.llm_client = llm_client

        # Build reverse lookup: synonym -> canonical
        self.reverse_lookup = {}
        for canonical, synonyms in self.mappings.items():
            # Canonical maps to itself
            self.reverse_lookup[canonical.lower()] = canonical
            # Each synonym maps to canonical
            for synonym in synonyms:
                self.reverse_lookup[synonym.lower()] = canonical

    def normalize(self, skill: str) -> str:
        """
        Normalize a skill name.

        Args:
            skill: Raw skill name (e.g., "Reactt", "js", "postgre sql")

        Returns:
            Normalized skill name (e.g., "React", "JavaScript", "PostgreSQL")

        Strategy:
        1. Try static lookup (exact match, case-insensitive)
        2. If not found and LLM available, use LLM for fuzzy matching
        3. Otherwise, return title-cased input
        """
        skill_lower = skill.lower().strip()

        # Static lookup
        if skill_lower in self.reverse_lookup:
            return self.reverse_lookup[skill_lower].title()

        # LLM fallback (if available)
        if self.llm_client:
            normalized = self._llm_normalize(skill)
            if normalized:
                return normalized

        # Default: title case the input
        return skill.strip().title()

    def _llm_normalize(self, skill: str) -> Optional[str]:
        """
        Use LLM to normalize skill (fuzzy matching).

        Args:
            skill: Raw skill name

        Returns:
            Normalized skill or None if LLM fails
        """
        if not self.llm_client:
            return None

        # Simple prompt for skill normalization
        prompt = f"""Normalize this technology/skill name to its canonical form:

Input: "{skill}"

Rules:
- Fix typos (e.g., "Reactt" -> "React")
- Use standard capitalization (e.g., "javascript" -> "JavaScript")
- Expand common abbreviations if clear (e.g., "js" -> "JavaScript", "k8s" -> "Kubernetes")
- Return ONLY the normalized name, no explanation

Normalized skill:"""

        try:
            response = self.llm_client.complete(prompt, max_tokens=20, temperature=0)
            normalized = response.strip()
            # Basic validation: should be short (< 50 chars)
            if len(normalized) < 50 and normalized:
                return normalized
        except Exception:
            # LLM failure, fall back to title case
            pass

        return None

    def normalize_list(self, skills: list[str]) -> list[str]:
        """
        Normalize a list of skills, removing duplicates.

        Args:
            skills: List of raw skill names

        Returns:
            List of normalized, deduplicated skills
        """
        normalized = [self.normalize(skill) for skill in skills]
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for skill in normalized:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill)
        return result
