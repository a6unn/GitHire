"""Integration tests for end-to-end search service.

Tests SearchService orchestrating GitHub search, profile enrichment, and caching.
Will FAIL until T019 (SearchService) is implemented.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


@pytest.mark.asyncio
async def test_search_service_imports():
    """Test that SearchService can be imported."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        assert SearchService is not None
    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_service_end_to_end():
    """SearchService should orchestrate search from JobRequirement to Candidates."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            role="Python Developer",
            required_skills=["Python", "FastAPI"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=3, max=None, range_text="3+ years"),
            location_preferences=["India"],
            confidence_scores={},
            original_input="Python developer with 3 years",
            schema_version="1.0.0"
        )

        # Mock dependencies
        mock_github_client = MagicMock()
        mock_github_client.search_users = AsyncMock(return_value=["user1", "user2"])
        mock_github_client.get_profile = AsyncMock(return_value={
            "login": "user1",
            "name": "Test User",
            "bio": "Developer",
            "location": "India",
            "email": None,
            "followers": 100,
            "created_at": "2020-01-01T00:00:00Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/1",
            "html_url": "https://github.com/user1"
        })
        mock_github_client.get_repos = AsyncMock(return_value=[
            {
                "name": "test-repo",
                "description": "Test",
                "stargazers_count": 50,
                "forks_count": 10,
                "language": "Python",
                "html_url": "https://github.com/user1/test-repo"
            }
        ])

        mock_cache = MagicMock()
        mock_cache.get_search_results = MagicMock(return_value=None)  # Cache miss
        mock_cache.set_search_results = MagicMock()
        mock_cache.set_profile = MagicMock()
        mock_cache.generate_cache_key = MagicMock(return_value="test_cache_key")

        service = SearchService(github_client=mock_github_client, cache_service=mock_cache)
        result = await service.search(job_req)

        # Verify output structure
        assert "candidates" in result
        assert "metadata" in result
        assert len(result["candidates"]) > 0
        assert result["metadata"].total_candidates_found >= 0
        assert result["metadata"].candidates_returned <= 25

    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_service_returns_max_25_candidates():
    """SearchService should return maximum 25 candidates."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            required_skills=["Python"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test",
            schema_version="1.0.0"
        )

        # Mock 50 users found
        usernames = [f"user{i}" for i in range(50)]

        mock_github_client = MagicMock()
        mock_github_client.search_users = AsyncMock(return_value=usernames)
        mock_github_client.get_profile = AsyncMock(return_value={
            "login": "user1",
            "name": "Test",
            "bio": None,
            "location": None,
            "email": None,
            "followers": 10,
            "created_at": "2020-01-01T00:00:00Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/1",
            "html_url": "https://github.com/user1"
        })
        mock_github_client.get_repos = AsyncMock(return_value=[])

        mock_cache = MagicMock()
        mock_cache.get_search_results = MagicMock(return_value=None)
        mock_cache.set_search_results = MagicMock()
        mock_cache.set_profile = MagicMock()
        mock_cache.generate_cache_key = MagicMock(return_value="key")

        service = SearchService(github_client=mock_github_client, cache_service=mock_cache)
        result = await service.search(job_req)

        # Should only return 25 candidates max
        assert len(result["candidates"]) <= 25

    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_service_cache_hit():
    """SearchService should use cached results when available."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        from src.github_sourcer.models.candidate import Candidate
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            required_skills=["Python"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test",
            schema_version="1.0.0"
        )

        cached_candidate = Candidate(
            github_username="cached_user",
            contribution_count=100,
            account_age_days=365,
            followers=50,
            profile_url="https://github.com/cached_user",
            top_repos=[],
            languages=["Python"],
            fetched_at=datetime.utcnow()
        )

        mock_github_client = MagicMock()
        # Should NOT be called if cache hit
        mock_github_client.search_users = AsyncMock(side_effect=Exception("Should not call API on cache hit"))

        mock_cache = MagicMock()
        mock_cache.get_search_results = MagicMock(return_value=["cached_user"])  # Cache HIT
        mock_cache.get_profile = MagicMock(return_value=cached_candidate)
        mock_cache.generate_cache_key = MagicMock(return_value="cached_key")

        service = SearchService(github_client=mock_github_client, cache_service=mock_cache)
        result = await service.search(job_req)

        # Should use cached data
        assert result["metadata"].cache_hit == True
        assert result["candidates"][0].github_username == "cached_user"

    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_service_partial_profile_failures():
    """SearchService should continue on partial profile fetch failures."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            required_skills=["Python"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test",
            schema_version="1.0.0"
        )

        mock_github_client = MagicMock()
        mock_github_client.search_users = AsyncMock(return_value=["user1", "user2", "user3"])

        # user1: success, user2: fails (404), user3: success
        call_count = 0

        async def mock_get_profile(username):
            nonlocal call_count
            call_count += 1
            if username == "user2":
                return None  # 404 - profile not found
            return {
                "login": username,
                "name": "Test",
                "bio": None,
                "location": None,
                "email": None,
                "followers": 10,
                "created_at": "2020-01-01T00:00:00Z",
                "avatar_url": f"https://avatars.githubusercontent.com/u/{call_count}",
                "html_url": f"https://github.com/{username}"
            }

        mock_github_client.get_profile = mock_get_profile
        mock_github_client.get_repos = AsyncMock(return_value=[])

        mock_cache = MagicMock()
        mock_cache.get_search_results = MagicMock(return_value=None)
        mock_cache.set_search_results = MagicMock()
        mock_cache.set_profile = MagicMock()
        mock_cache.generate_cache_key = MagicMock(return_value="key")

        service = SearchService(github_client=mock_github_client, cache_service=mock_cache)
        result = await service.search(job_req)

        # Should return 2 candidates (user1 and user3), skip user2
        assert len(result["candidates"]) == 2
        usernames = [c.github_username for c in result["candidates"]]
        assert "user1" in usernames
        assert "user3" in usernames
        assert "user2" not in usernames

    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_service_no_results_returns_empty_with_warning():
    """SearchService should return empty candidates list with warning when no results."""
    try:
        from src.github_sourcer.services.search_service import SearchService
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            required_skills=["NonexistentLanguage"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test",
            schema_version="1.0.0"
        )

        mock_github_client = MagicMock()
        mock_github_client.search_users = AsyncMock(return_value=[])  # No results

        mock_cache = MagicMock()
        mock_cache.get_search_results = MagicMock(return_value=None)
        mock_cache.generate_cache_key = MagicMock(return_value="key")

        service = SearchService(github_client=mock_github_client, cache_service=mock_cache)
        result = await service.search(job_req)

        assert result["candidates"] == []
        assert result["metadata"].total_candidates_found == 0
        assert result["metadata"].candidates_returned == 0
        assert len(result["metadata"].warnings) > 0  # Should have warning

    except ImportError as e:
        pytest.fail(f"SearchService not implemented yet: {e}")
