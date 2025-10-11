"""Configuration for GitHub Sourcer module.

Loads environment variables for GitHub API authentication and Redis connection.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Configuration singleton for GitHub Sourcer."""

    # GitHub API
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_API_BASE: str = os.getenv("GITHUB_API_BASE", "https://api.github.com")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Cache TTL (1 hour)
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # Rate limiting
    RATE_LIMIT_THRESHOLD: int = int(os.getenv("RATE_LIMIT_THRESHOLD", "10"))

    # HTTP timeouts
    HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "30.0"))

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration.

        Raises:
            ValueError: If required configuration is missing.
        """
        if not cls.GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required. "
                "Set it in .env or export GITHUB_TOKEN=ghp_..."
            )


# Validate configuration on import
# Comment out for tests that don't need GitHub token
try:
    Config.validate()
except ValueError:
    # Allow import without token for unit tests
    pass
