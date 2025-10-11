"""Integration tests for caching behavior.

Tests CacheService with mocked Redis.
Will FAIL until T017 (CacheService) is implemented.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json


@pytest.mark.asyncio
async def test_cache_service_imports():
    """Test that CacheService can be imported."""
    try:
        from src.github_sourcer.services.cache_service import CacheService
        assert CacheService is not None
    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_service_set_and_get_search_results():
    """CacheService should store and retrieve search results."""
    try:
        from src.github_sourcer.services.cache_service import CacheService

        # Mock Redis client
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(["user1", "user2", "user3"]).encode()
        mock_redis.setex.return_value = True

        cache = CacheService(redis_client=mock_redis)

        # Set search results
        cache.set_search_results("cache_key_123", ["user1", "user2", "user3"], ttl=3600)

        # Verify setex was called with correct arguments
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "search:cache_key_123"  # Key prefix
        assert call_args[0][1] == 3600  # TTL
        assert "user1" in call_args[0][2]  # Data

        # Get search results
        results = cache.get_search_results("cache_key_123")
        assert results == ["user1", "user2", "user3"]

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_service_get_nonexistent_key_returns_none():
    """Getting non-existent cache key should return None."""
    try:
        from src.github_sourcer.services.cache_service import CacheService

        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # Key doesn't exist

        cache = CacheService(redis_client=mock_redis)
        results = cache.get_search_results("nonexistent_key")

        assert results is None

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_service_set_and_get_profile():
    """CacheService should store and retrieve candidate profiles."""
    try:
        from src.github_sourcer.services.cache_service import CacheService
        from src.github_sourcer.models.candidate import Candidate

        candidate = Candidate(
            github_username="testuser",
            contribution_count=100,
            account_age_days=365,
            followers=50,
            profile_url="https://github.com/testuser",
            top_repos=[],
            languages=["Python"],
            fetched_at=datetime(2025, 10, 6, 10, 30, 0)
        )

        mock_redis = MagicMock()
        mock_redis.get.return_value = candidate.model_dump_json().encode()
        mock_redis.setex.return_value = True

        cache = CacheService(redis_client=mock_redis)

        # Set profile
        cache.set_profile("testuser", candidate, ttl=3600)

        # Verify setex was called
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "profile:testuser"
        assert call_args[0][1] == 3600

        # Get profile
        retrieved = cache.get_profile("testuser")
        assert retrieved.github_username == "testuser"
        assert retrieved.languages == ["Python"]

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_key_generation_deterministic():
    """Cache key generation should be deterministic for same input."""
    try:
        from src.github_sourcer.services.cache_service import CacheService
        # Assuming we need JobRequirement for key generation
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req = JobRequirement(
            required_skills=["Python", "FastAPI"],
            preferred_skills=["Docker"],
            years_of_experience=YearsOfExperience(min=5, max=None, range_text="5+ years"),
            location_preferences=["India"],
            confidence_scores={},
            original_input="test",
            schema_version="1.0.0"
        )

        cache = CacheService()
        key1 = cache.generate_cache_key(job_req)
        key2 = cache.generate_cache_key(job_req)

        # Same input should generate same key
        assert key1 == key2
        assert len(key1) > 0

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_key_different_for_different_inputs():
    """Cache key should differ for different job requirements."""
    try:
        from src.github_sourcer.services.cache_service import CacheService
        from src.jd_parser.models import JobRequirement, YearsOfExperience

        job_req1 = JobRequirement(
            required_skills=["Python"],
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test1",
            schema_version="1.0.0"
        )

        job_req2 = JobRequirement(
            required_skills=["JavaScript"],  # Different skill
            preferred_skills=[],
            years_of_experience=YearsOfExperience(min=None, max=None, range_text=None),
            location_preferences=[],
            confidence_scores={},
            original_input="test2",
            schema_version="1.0.0"
        )

        cache = CacheService()
        key1 = cache.generate_cache_key(job_req1)
        key2 = cache.generate_cache_key(job_req2)

        # Different inputs should generate different keys
        assert key1 != key2

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")


def test_cache_ttl_set_correctly():
    """Cache should respect TTL (time-to-live) settings."""
    try:
        from src.github_sourcer.services.cache_service import CacheService

        mock_redis = MagicMock()
        cache = CacheService(redis_client=mock_redis)

        # Set with custom TTL
        cache.set_search_results("test_key", ["user1"], ttl=7200)

        # Verify TTL was set to 7200 seconds (2 hours)
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 7200

    except ImportError as e:
        pytest.fail(f"CacheService not implemented yet: {e}")
