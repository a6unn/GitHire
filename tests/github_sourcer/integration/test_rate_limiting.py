"""
Integration Tests for RateLimiter (T011)
==========================================
Tests for GitHub API rate limiting behavior.

TDD Approach: These tests WILL FAIL until RateLimiter is implemented.

Specification Reference: modules/002-github-sourcer-module/tasks.md T011
"""

import pytest
import time
from unittest.mock import Mock, AsyncMock
from src.github_sourcer.lib.rate_limiter import RateLimiter, RateLimitExceeded


class TestRateLimiter:
    """Integration tests for rate limiting behavior"""

    def test_rate_limiter_initialization(self):
        """Test that RateLimiter can be instantiated"""
        rate_limiter = RateLimiter()
        assert rate_limiter is not None

    def test_check_quota_with_sufficient_remaining(self):
        """Test that sufficient quota allows operation to proceed"""
        rate_limiter = RateLimiter()

        # Mock response headers with plenty of quota remaining
        headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        # Should not raise any exception
        rate_limiter.check_quota(headers)

    def test_check_quota_with_low_remaining_waits(self):
        """Test that low quota (< 10) triggers wait until reset time"""
        rate_limiter = RateLimiter()

        # Mock response headers with low quota (should trigger wait)
        # Set reset time to 2 seconds in future for quick test
        reset_time = int(time.time()) + 2
        headers = {
            "X-RateLimit-Remaining": "5",  # Less than 10
            "X-RateLimit-Reset": str(reset_time)
        }

        start_time = time.time()

        # This should wait until reset time
        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limiter.check_quota(headers)

        # Verify error message mentions waiting
        assert "rate limit" in str(exc_info.value).lower()

    def test_check_quota_with_zero_remaining_raises_error(self):
        """Test that zero remaining quota raises RateLimitExceeded"""
        rate_limiter = RateLimiter()

        headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        with pytest.raises(RateLimitExceeded) as exc_info:
            rate_limiter.check_quota(headers)

        assert "rate limit exceeded" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_exponential_backoff_on_403(self):
        """Test exponential backoff on 403 response (2s, 4s, 8s)"""
        rate_limiter = RateLimiter()

        # Simulate 403 response
        response = Mock()
        response.status_code = 403
        response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        # First retry: should wait ~2 seconds
        start_time = time.time()
        with pytest.raises(RateLimitExceeded):
            await rate_limiter.handle_rate_limit_response(response, retry_count=1)
        elapsed = time.time() - start_time

        # Should have waited approximately 2 seconds (allow some tolerance)
        assert 1.5 <= elapsed <= 3.0, f"Expected ~2s wait, got {elapsed}s"

    @pytest.mark.asyncio
    async def test_max_retries_respected(self):
        """Test that maximum 3 retries are attempted"""
        rate_limiter = RateLimiter(max_retries=3)

        response = Mock()
        response.status_code = 403
        response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        # After 3 retries, should raise error without retrying further
        with pytest.raises(RateLimitExceeded) as exc_info:
            await rate_limiter.handle_rate_limit_response(response, retry_count=3)

        assert "max retries" in str(exc_info.value).lower()

    def test_missing_rate_limit_headers_handled_gracefully(self):
        """Test that missing rate limit headers don't crash"""
        rate_limiter = RateLimiter()

        # Headers without rate limit info
        headers = {}

        # Should handle gracefully, possibly with warning
        # Should not raise exception for missing headers
        try:
            rate_limiter.check_quota(headers)
        except KeyError:
            pytest.fail("RateLimiter should handle missing headers gracefully")

    def test_rate_limit_warning_logged(self, caplog):
        """Test that warnings are logged when rate limit is low"""
        rate_limiter = RateLimiter()

        headers = {
            "X-RateLimit-Remaining": "8",  # Low but not zero
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        # Should log warning
        with caplog.at_level("WARNING"):
            rate_limiter.check_quota(headers)

        # Check that warning was logged
        assert any("rate limit" in record.message.lower() for record in caplog.records)

    def test_rate_limit_info_tracking(self):
        """Test that rate limit info is tracked and accessible"""
        rate_limiter = RateLimiter()

        headers = {
            "X-RateLimit-Remaining": "50",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }

        rate_limiter.check_quota(headers)

        # Should be able to access current rate limit status
        status = rate_limiter.get_status()
        assert status["remaining"] == 50
        assert status["limit"] == 60
