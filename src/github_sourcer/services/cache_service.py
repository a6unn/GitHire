"""Cache service for GitHub search results and profiles.

Two-tier caching: search results (usernames) and individual profiles.
"""

import redis
import json
import hashlib
import logging
from typing import Optional, List, Dict
from src.github_sourcer.models.candidate import Candidate
from src.github_sourcer.config import Config

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based cache for search results and candidate profiles with in-memory fallback."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize cache service.

        Args:
            redis_client: Redis client instance (creates new one if None)
        """
        # In-memory fallback cache when Redis is unavailable
        self._memory_cache: Dict[str, any] = {}

        if redis_client is None:
            try:
                self.redis = redis.from_url(
                    Config.REDIS_URL,
                    db=Config.REDIS_DB,
                    decode_responses=True  # Automatically decode bytes to strings
                )
                # Test connection
                self.redis.ping()
                logger.info(f"Connected to Redis at {Config.REDIS_URL}")
            except (redis.ConnectionError, redis.RedisError) as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache fallback.")
                self.redis = None
        else:
            self.redis = redis_client

    def get_search_results(self, cache_key: str) -> Optional[List[str]]:
        """
        Get cached search results (usernames).

        Args:
            cache_key: Cache key for search criteria

        Returns:
            List of usernames or None if not cached
        """
        if not self.redis:
            return None

        try:
            key = f"search:{cache_key}"
            data = self.redis.get(key)

            if data:
                usernames = json.loads(data)
                logger.debug(f"Cache HIT for search: {cache_key}")
                return usernames

            logger.debug(f"Cache MISS for search: {cache_key}")
            return None

        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error reading from cache: {e}")
            return None

    def set_search_results(self, cache_key: str, usernames: List[str], ttl: int = 3600) -> None:
        """
        Cache search results (usernames).

        Args:
            cache_key: Cache key for search criteria
            usernames: List of GitHub usernames
            ttl: Time-to-live in seconds (default: 3600 = 1 hour)
        """
        if not self.redis:
            return

        try:
            key = f"search:{cache_key}"
            data = json.dumps(usernames)
            self.redis.setex(key, ttl, data)
            logger.debug(f"Cached search results: {cache_key} ({len(usernames)} users, TTL={ttl}s)")

        except redis.RedisError as e:
            logger.error(f"Error writing to cache: {e}")

    def get_profile(self, username: str) -> Optional[Candidate]:
        """
        Get cached candidate profile.

        Args:
            username: GitHub username

        Returns:
            Candidate object or None if not cached
        """
        key = f"profile:{username}"

        # Try Redis first
        if self.redis:
            try:
                data = self.redis.get(key)

                if data:
                    # Parse JSON to Candidate object
                    candidate = Candidate.model_validate_json(data)
                    logger.debug(f"Cache HIT (Redis) for profile: {username}")
                    return candidate

            except (redis.RedisError, Exception) as e:
                logger.error(f"Error reading profile from Redis: {e}")

        # Fallback to memory cache
        if key in self._memory_cache:
            logger.debug(f"Cache HIT (memory) for profile: {username}")
            return self._memory_cache[key]

        logger.debug(f"Cache MISS for profile: {username}")
        return None

    def set_profile(self, username: str, candidate: Candidate, ttl: int = 3600) -> None:
        """
        Cache candidate profile.

        Args:
            username: GitHub username
            candidate: Candidate object
            ttl: Time-to-live in seconds (default: 3600 = 1 hour)
        """
        key = f"profile:{username}"

        # Try Redis first
        if self.redis:
            try:
                data = candidate.model_dump_json()
                self.redis.setex(key, ttl, data)
                logger.debug(f"Cached profile (Redis): {username} (TTL={ttl}s)")
                return  # Successfully cached in Redis
            except redis.RedisError as e:
                logger.error(f"Error writing profile to Redis: {e}")

        # Fallback to memory cache
        self._memory_cache[key] = candidate
        logger.debug(f"Cached profile (memory): {username}")

    def generate_cache_key(self, job_req) -> str:
        """
        Generate deterministic cache key from JobRequirement.

        Args:
            job_req: JobRequirement from Module 001

        Returns:
            SHA256 hash (first 16 chars) of normalized job requirements
        """
        # Create deterministic representation
        criteria = {
            "required_skills": sorted(job_req.required_skills),
            "preferred_skills": sorted(job_req.preferred_skills),
            "location": sorted(job_req.location_preferences),
            "seniority": job_req.seniority_level,
            "min_experience": job_req.years_of_experience.min if job_req.years_of_experience else None
        }

        # Sort keys and create JSON
        hash_input = json.dumps(criteria, sort_keys=True)

        # Generate SHA256 hash
        hash_obj = hashlib.sha256(hash_input.encode())
        cache_key = hash_obj.hexdigest()[:16]  # First 16 chars

        logger.debug(f"Generated cache key: {cache_key} for criteria: {criteria}")
        return cache_key
