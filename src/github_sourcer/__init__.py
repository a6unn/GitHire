"""GitHub Sourcer Module (Module 002).

Main entry point for searching GitHub developers based on job requirements.
ENHANCED with LocationParser, SkillDetector, and EnsembleScorer.
"""

# Models
from src.github_sourcer.models.candidate import Candidate, Repository
from src.github_sourcer.models.search_result import SearchResult
from src.github_sourcer.models.search_criteria import SearchCriteria
from src.github_sourcer.models.location_hierarchy import LocationHierarchy
from src.github_sourcer.models.skill_confidence import SkillConfidence
from src.github_sourcer.models.candidate_score import CandidateScore

# Services
from src.github_sourcer.services.search_service import SearchService
from src.github_sourcer.services.github_client import GitHubClient
from src.github_sourcer.services.cache_service import CacheService
from src.github_sourcer.services.profile_enricher import ProfileEnricher
from src.github_sourcer.services.location_parser import LocationParser
from src.github_sourcer.services.skill_detector import SkillDetector
from src.github_sourcer.services.ensemble_scorer import EnsembleScorer

# Libraries
from src.github_sourcer.lib.fuzzy_matcher import FuzzyMatcher
from src.github_sourcer.lib.config_loader import ConfigLoader
from src.github_sourcer.lib.rate_limiter import RateLimiter


# Global singletons for connection pooling (optional optimization)
_github_client = None
_cache_service = None


def get_github_client() -> GitHubClient:
    """
    Get or create singleton GitHub client with connection pooling.

    Returns:
        GitHubClient instance
    """
    global _github_client
    if _github_client is None:
        _github_client = GitHubClient()
    return _github_client


def get_cache_service() -> CacheService:
    """
    Get or create singleton cache service.

    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# Convenience function for simple usage
async def search_github(job_requirement) -> dict:
    """
    Search GitHub for candidates matching job requirements.

    Convenience function that creates a SearchService and performs search.

    Args:
        job_requirement: JobRequirement from Module 001

    Returns:
        Dict with:
            - candidates: List[Candidate] (max 25)
            - metadata: SearchResult

    Example:
        ```python
        from src.github_sourcer import search_github
        from src.jd_parser.models import JobRequirement

        job_req = JobRequirement(
            required_skills=["Python", "FastAPI"],
            location_preferences=["India"],
            ...
        )

        result = await search_github(job_req)
        print(f"Found {len(result['candidates'])} candidates")
        ```
    """
    service = SearchService()
    return await service.search(job_requirement)


__all__ = [
    # Models
    "Candidate",
    "Repository",
    "SearchResult",
    "SearchCriteria",
    "LocationHierarchy",
    "SkillConfidence",
    "CandidateScore",
    # Services
    "SearchService",
    "GitHubClient",
    "CacheService",
    "ProfileEnricher",
    "LocationParser",
    "SkillDetector",
    "EnsembleScorer",
    # Libraries
    "FuzzyMatcher",
    "ConfigLoader",
    "RateLimiter",
    # Singleton helpers
    "get_github_client",
    "get_cache_service",
    # Convenience function
    "search_github",
]


__version__ = "0.1.0"
