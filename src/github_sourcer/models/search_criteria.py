"""SearchCriteria model for processing job requirements into GitHub queries.

Internal entity that maps JobRequirement to GitHub search parameters.
"""

from pydantic import BaseModel, Field
from typing import Optional
import json
from src.github_sourcer.services.location_parser import LocationParser


# Skill to GitHub language mapping (reuse from Module 001 concept)
SKILL_TO_GITHUB_LANGUAGE = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "react": "javascript",  # React uses JavaScript
    "vue": "javascript",
    "angular": "typescript",
    "node.js": "javascript",
    "nodejs": "javascript",
    "java": "java",
    "spring": "java",
    "kotlin": "kotlin",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",
    "csharp": "c#",
    ".net": "c#",
    "dotnet": "c#",
    "vb .net": "c#",
    "vb.net": "c#",
    "asp .net": "c#",
    "asp.net": "c#",
    "asp.net core": "c#",
    "ruby": "ruby",
    "rails": "ruby",
    "php": "php",
    "laravel": "php",
    "swift": "swift",
    "objective-c": "objective-c",
    "r": "r",
    "scala": "scala",
    "shell": "shell",
    "bash": "shell",
    "powershell": "powershell",
    "sql": "sql",
    "postgresql": "plpgsql",
    "mysql": "sql",
    "mongodb": "javascript",  # MongoDB commonly used with JS
    "redis": "shell",
    "docker": "dockerfile",
    "kubernetes": "yaml",
}


class SearchCriteria(BaseModel):
    """Internal representation of search parameters."""

    required_languages: list[str] = Field(
        default_factory=list, description="Programming languages from required_skills"
    )
    preferred_languages: list[str] = Field(
        default_factory=list, description="Programming languages from preferred_skills"
    )
    location_filter: Optional[str] = Field(
        None, description="Location filter (broadened to country if specific)"
    )
    min_account_age_days: Optional[int] = Field(
        None, ge=0, description="Minimum account age (estimated from years_of_experience)"
    )
    activity_level: Optional[str] = Field(
        None,
        pattern="^(low|medium|high)$",
        description="Expected activity level (from seniority_level)",
    )

    # GitHub API query string
    query_string: str = Field(..., min_length=1, description="Constructed GitHub search query")

    @classmethod
    def from_job_requirement(cls, job_req) -> "SearchCriteria":
        """
        Construct SearchCriteria from JobRequirement.

        Args:
            job_req: JobRequirement from Module 001

        Returns:
            SearchCriteria with GitHub query constructed
        """
        # Map skills to GitHub languages
        required_langs = [
            SKILL_TO_GITHUB_LANGUAGE.get(skill.lower(), skill.lower())
            for skill in job_req.required_skills
        ]

        preferred_langs = [
            SKILL_TO_GITHUB_LANGUAGE.get(skill.lower(), skill.lower())
            for skill in job_req.preferred_skills
        ]

        # Extract city or state for location search (prioritize specificity)
        location = None
        if job_req.location_preferences:
            location = cls._extract_city_or_state(job_req.location_preferences)

        # Estimate min account age from experience
        min_age_days = None
        if job_req.years_of_experience and job_req.years_of_experience.min:
            min_age_days = job_req.years_of_experience.min * 365

        # Map seniority to activity level
        activity_level = cls._map_seniority_to_activity(job_req.seniority_level)

        # Build GitHub query string
        query = cls._build_query(
            required_langs=required_langs,
            preferred_langs=preferred_langs,
            location=location,
        )

        return cls(
            required_languages=required_langs,
            preferred_languages=preferred_langs,
            location_filter=location,
            min_account_age_days=min_age_days,
            activity_level=activity_level,
            query_string=query,
        )

    @staticmethod
    def _build_query(
        required_langs: list[str], preferred_langs: list[str], location: Optional[str]
    ) -> str:
        """Build GitHub search query string."""
        query_parts = []

        # Use primary language from required skills
        if required_langs:
            query_parts.append(f"language:{required_langs[0]}")
        elif preferred_langs:
            query_parts.append(f"language:{preferred_langs[0]}")

        if location:
            query_parts.append(f"location:{location}")

        # Filter to individual users only (exclude organizations)
        query_parts.append("type:user")

        # Use GitHub's default relevance sorting (removed sort:followers)
        # This prioritizes actual developers over popular accounts/companies

        # If no query parts (except type:user), use a generic search
        if not query_parts or query_parts == ["type:user"]:
            return "type:user"

        return " ".join(query_parts)

    @staticmethod
    def _extract_city_or_state(locations: list[str]) -> str:
        """
        Extract city or state from location list using LocationParser.

        Prioritizes specificity: city > state > country
        This enables progressive broadening in search service.

        Args:
            locations: List of location strings from job requirements

        Returns:
            Most specific location component (city or state)
        """
        if not locations:
            return "remote"

        # Use LocationParser to parse the first location
        location_parser = LocationParser()
        parsed_location = location_parser.parse_location(locations[0])

        # Return the most specific available location component
        # Priority: city > state > country
        if parsed_location.city:
            return parsed_location.city.lower()
        elif parsed_location.state:
            # For state-level search, return as-is
            # The search service will handle broadening to country
            return parsed_location.state.lower()
        elif parsed_location.country:
            return parsed_location.country.lower()

        # Fallback: return original location string
        return locations[0].lower()

    @staticmethod
    def _map_seniority_to_activity(seniority: Optional[str]) -> Optional[str]:
        """Map seniority level to expected activity."""
        if not seniority:
            return None

        mapping = {
            "Junior": "low",
            "Mid-level": "medium",
            "Senior": "high",
            "Staff": "high",
            "Principal": "high",
        }
        return mapping.get(seniority)
