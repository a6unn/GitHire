"""Rate limiter for GitHub API quota management.

Handles GitHub API rate limits with exponential backoff and quota tracking.
"""

import time
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when GitHub API rate limit is exceeded."""
    pass


class RateLimiter:
    """Manages GitHub API rate limiting with exponential backoff."""

    def __init__(self, threshold: int = 10, max_retries: int = 3):
        """
        Initialize RateLimiter.

        Args:
            threshold: Minimum remaining requests before pausing (default: 10)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.threshold = threshold
        self.max_retries = max_retries
        self.MAX_RETRIES = max_retries  # Alias for compatibility
        self._status = {
            "remaining": None,
            "limit": None,
            "reset": None
        }

    def check_quota(self, headers: Dict[str, str]) -> None:
        """
        Check rate limit quota and pause if necessary.

        Args:
            headers: Response headers from GitHub API

        Raises:
            RateLimitExceeded: If rate limit is exceeded (remaining == 0)

        Pauses execution if remaining quota is below threshold.
        """
        try:
            remaining = self.get_remaining(headers)
            reset_time = self.get_reset_time(headers)
            limit = headers.get("X-RateLimit-Limit")

            # Update status for tracking
            self._status["remaining"] = remaining
            self._status["limit"] = int(limit) if limit else None
            self._status["reset"] = reset_time

            # If rate limit is completely exhausted, raise exception
            if remaining == 0:
                raise RateLimitExceeded("Rate limit exceeded. Remaining quota is 0.")

            # Warn if low but not zero
            if remaining < self.threshold:
                logger.warning(
                    f"Rate limit low ({remaining} remaining). "
                    f"Consider waiting until reset at {reset_time}."
                )
                # Only raise if truly at zero
                if remaining <= 5:
                    raise RateLimitExceeded(
                        f"Rate limit critically low ({remaining} remaining). "
                        f"Resets at {reset_time}."
                    )

        except (KeyError, ValueError, TypeError) as e:
            # Missing or invalid headers - continue without blocking
            logger.debug(f"Could not parse rate limit headers: {e}")

    def get_remaining(self, headers: Dict[str, str]) -> int:
        """
        Extract remaining quota from headers.

        Args:
            headers: Response headers

        Returns:
            Remaining API quota (defaults to 5000 if header missing)
        """
        try:
            return int(headers.get("X-RateLimit-Remaining", 5000))
        except (ValueError, TypeError):
            return 5000

    def get_reset_time(self, headers: Dict[str, str]) -> int:
        """
        Extract reset timestamp from headers.

        Args:
            headers: Response headers

        Returns:
            Unix timestamp when quota resets (defaults to current time if missing)
        """
        try:
            return int(headers.get("X-RateLimit-Reset", int(time.time())))
        except (ValueError, TypeError):
            return int(time.time())

    async def handle_rate_limit_error(self, attempt: int) -> None:
        """
        Handle 403 rate limit error with exponential backoff.

        Args:
            attempt: Current retry attempt number (0-indexed)

        Waits for 2^attempt seconds before retrying.
        """
        if attempt >= self.max_retries:
            raise Exception(f"Max retries ({self.max_retries}) exceeded for rate limit")

        # Exponential backoff: 2^0 = 1s, 2^1 = 2s, 2^2 = 4s
        wait_seconds = 2**attempt
        logger.warning(f"Rate limit hit. Retry {attempt + 1}/{self.max_retries}. Waiting {wait_seconds}s...")

        await asyncio.sleep(wait_seconds)

    async def handle_rate_limit_response(self, response, retry_count: int) -> None:
        """
        Handle rate limit response with exponential backoff.

        Args:
            response: HTTP response object with status_code and headers
            retry_count: Current retry count (1-indexed)

        Raises:
            RateLimitExceeded: If max retries exceeded or rate limit hit
        """
        if retry_count > self.max_retries:
            raise RateLimitExceeded(
                f"Max retries ({self.max_retries}) exceeded for rate limit"
            )

        # Exponential backoff: retry 1 = 2s, retry 2 = 4s, retry 3 = 8s
        wait_seconds = 2 ** retry_count
        logger.warning(
            f"Rate limit (403). Retry {retry_count}/{self.max_retries}. "
            f"Waiting {wait_seconds}s..."
        )

        await asyncio.sleep(wait_seconds)
        raise RateLimitExceeded(
            f"Max retries ({self.max_retries}) exceeded after {wait_seconds}s backoff"
        )

    def get_status(self) -> Dict:
        """
        Get current rate limit status.

        Returns:
            Dictionary with remaining, limit, and reset fields
        """
        return self._status.copy()
