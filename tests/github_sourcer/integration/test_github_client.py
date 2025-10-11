"""
Integration Tests for GitHubClient (T007, T008)
================================================
Tests for GitHub API client (search users, fetch profiles, fetch repos).

TDD Approach: These tests WILL FAIL until GitHubClient is implemented.

Specification Reference: modules/002-github-sourcer-module/tasks.md T007, T008
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.github_sourcer.services.github_client import GitHubClient, GitHubAPIError


class TestGitHubClientSearch:
    """Integration tests for GitHub user search (T007)"""

    @pytest.mark.asyncio
    async def test_github_client_initialization(self):
        """Test that GitHubClient can be instantiated"""
        client = GitHubClient(token="test_token")
        assert client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_search_users_returns_usernames(self):
        """Test search for language:python location:india returns users"""
        client = GitHubClient(token="test_token")

        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = {
            "items": [
                {"login": "user1"},
                {"login": "user2"},
                {"login": "user3"}
            ]
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            usernames = await client.search_users("language:python location:india")

            assert len(usernames) == 3
            assert "user1" in usernames
            assert "user2" in usernames
            assert "user3" in usernames

        await client.close()

    @pytest.mark.asyncio
    async def test_search_users_empty_query_raises_error(self):
        """Test that empty search query raises ValueError"""
        client = GitHubClient(token="test_token")

        with pytest.raises(ValueError) as exc_info:
            await client.search_users("")

        assert "query" in str(exc_info.value).lower()
        await client.close()

    @pytest.mark.asyncio
    async def test_search_users_rate_limit_triggers_backoff(self):
        """Test that 403 rate limit triggers exponential backoff"""
        client = GitHubClient(token="test_token")

        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "9999999999"
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            with pytest.raises(GitHubAPIError) as exc_info:
                await client.search_users("language:python")

            assert "rate limit" in str(exc_info.value).lower()

        await client.close()

    @pytest.mark.asyncio
    async def test_search_users_handles_pagination(self):
        """Test that search handles paginated results"""
        client = GitHubClient(token="test_token")

        # Mock response with pagination
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = {
            "items": [{"login": f"user{i}"} for i in range(30)]
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            usernames = await client.search_users("language:python", max_results=50)

            # Should return 30 users (one page)
            assert len(usernames) == 30

        await client.close()


class TestGitHubClientProfile:
    """Integration tests for profile fetching (T008)"""

    @pytest.mark.asyncio
    async def test_get_profile_returns_user_data(self):
        """Test fetch profile for 'torvalds' returns complete data"""
        client = GitHubClient(token="test_token")

        # Mock user profile response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = {
            "login": "torvalds",
            "name": "Linus Torvalds",
            "bio": "Creator of Linux",
            "location": "Portland, OR",
            "email": None,
            "public_repos": 5,
            "followers": 150000,
            "created_at": "2011-09-03T15:26:22Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
            "html_url": "https://github.com/torvalds"
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            profile = await client.get_profile("torvalds")

            assert profile["login"] == "torvalds"
            assert profile["name"] == "Linus Torvalds"
            assert profile["public_repos"] == 5
            assert profile["followers"] == 150000

        await client.close()

    @pytest.mark.asyncio
    async def test_get_repos_returns_repository_list(self):
        """Test fetch repos returns list of repositories"""
        client = GitHubClient(token="test_token")

        # Mock repos response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = [
            {
                "name": "linux",
                "description": "Linux kernel source tree",
                "stargazers_count": 150000,
                "forks_count": 50000,
                "language": "C",
                "html_url": "https://github.com/torvalds/linux"
            },
            {
                "name": "test",
                "description": "Test repo",
                "stargazers_count": 10,
                "forks_count": 2,
                "language": "Shell",
                "html_url": "https://github.com/torvalds/test"
            }
        ]

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            repos = await client.get_repos("torvalds")

            assert len(repos) == 2
            assert repos[0]["name"] == "linux"
            assert repos[0]["stargazers_count"] == 150000
            assert repos[1]["name"] == "test"

        await client.close()

    @pytest.mark.asyncio
    async def test_get_profile_404_returns_none(self):
        """Test that 404 for private profile returns None"""
        client = GitHubClient(token="test_token")

        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            profile = await client.get_profile("nonexistentuser999")

            assert profile is None

        await client.close()

    @pytest.mark.asyncio
    async def test_get_repos_with_no_repos_returns_empty_list(self):
        """Test that profile with no repos returns empty list"""
        client = GitHubClient(token="test_token")

        # Mock empty repos response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = []

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            repos = await client.get_repos("userwithnorepos")

            assert repos == []

        await client.close()

    @pytest.mark.asyncio
    async def test_client_uses_authorization_header(self):
        """Test that client includes Authorization header with token"""
        client = GitHubClient(token="ghp_test123")

        # Verify Authorization header is set in the client
        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == "token ghp_test123"

        await client.close()

    @pytest.mark.asyncio
    async def test_client_respects_timeout(self):
        """Test that client respects timeout setting"""
        client = GitHubClient(token="test_token", timeout=10.0)

        assert client.timeout == 10.0
        await client.close()

    @pytest.mark.asyncio
    async def test_batch_get_profiles_graphql(self):
        """Test GraphQL batching for multiple profiles (T011D)"""
        client = GitHubClient(token="test_token")

        # Mock GraphQL response for batch query
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = {
            "data": {
                "user0": {"login": "user1", "name": "User One"},
                "user1": {"login": "user2", "name": "User Two"},
                "user2": {"login": "user3", "name": "User Three"}
            }
        }

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            usernames = ["user1", "user2", "user3"]
            profiles = await client.batch_get_profiles_graphql(usernames)

            assert len(profiles) == 3
            assert profiles[0]["login"] == "user1"
            assert profiles[1]["login"] == "user2"

        await client.close()

    @pytest.mark.asyncio
    async def test_get_dependency_graph(self):
        """Test fetching dependency graph for skills detection (T016)"""
        client = GitHubClient(token="test_token")

        # Mock dependency graph response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "100",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Reset": "9999999999"
        }
        mock_response.json.return_value = {
            "dependencies": [
                {"package_name": "pandas", "requirements": ">=1.0.0"},
                {"package_name": "numpy", "requirements": ">=1.20.0"}
            ]
        }

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            deps = await client.get_dependency_graph("user1", "myrepo")

            assert "dependencies" in deps
            assert len(deps["dependencies"]) == 2

        await client.close()

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test that client works as async context manager"""
        async with GitHubClient(token="test_token") as client:
            assert client is not None

        # Client should be closed after context exit
        assert client.client is None or hasattr(client, '_closed')
