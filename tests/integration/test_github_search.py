"""Integration tests for GitHub user search.

Tests GitHubClient search_users method with mocked responses.
Will FAIL until T016 (GitHubClient) is implemented.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


@pytest.mark.asyncio
async def test_github_client_imports():
    """Test that GitHubClient can be imported."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient
        assert GitHubClient is not None
    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_users_returns_usernames():
    """search_users should return list of usernames."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        # Mock httpx response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 3,
            "items": [
                {"login": "user1"},
                {"login": "user2"},
                {"login": "user3"}
            ]
        }
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = GitHubClient(token="fake_token")
            usernames = await client.search_users("language:python location:india")

            assert usernames == ["user1", "user2", "user3"]

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_users_with_empty_query_raises_error():
    """Empty search query should raise ValueError."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        client = GitHubClient(token="fake_token")

        with pytest.raises(ValueError) as exc_info:
            await client.search_users("")

        assert "query" in str(exc_info.value).lower()

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_users_rate_limit_403_triggers_backoff():
    """Rate limit (403) should trigger exponential backoff."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        # Mock 403 response
        mock_response_403 = MagicMock()
        mock_response_403.status_code = 403
        mock_response_403.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890"
        }

        # Mock success response after retry
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "total_count": 1,
            "items": [{"login": "user1"}]
        }
        mock_response_200.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_response_403  # First call fails
            return mock_response_200  # Second call succeeds

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=mock_get):
            with patch("asyncio.sleep", new_callable=AsyncMock):  # Mock sleep to avoid delays
                client = GitHubClient(token="fake_token")
                usernames = await client.search_users("language:python")

                # Should retry and eventually succeed
                assert usernames == ["user1"]
                assert call_count == 2  # Called twice (1 failure + 1 success)

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_users_no_results_returns_empty_list():
    """Search with no results should return empty list."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_count": 0,
            "items": []
        }
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = GitHubClient(token="fake_token")
            usernames = await client.search_users("language:nonexistent")

            assert usernames == []

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_search_users_includes_auth_header():
    """search_users should include Authorization header."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total_count": 0, "items": []}
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        mock_get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient.get", mock_get):
            client = GitHubClient(token="test_token_123")
            await client.search_users("language:python")

            # Verify Authorization header was included
            call_args = mock_get.call_args
            headers = call_args[1].get("headers", {}) if call_args else {}
            assert "Authorization" in headers
            assert "test_token_123" in headers["Authorization"]

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")
