"""Integration tests for profile enrichment.

Tests profile fetching and enrichment logic.
Will FAIL until T016 (GitHubClient) and T018 (ProfileEnricher) are implemented.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


@pytest.mark.asyncio
async def test_github_client_get_profile():
    """get_profile should fetch user data from GitHub API."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "torvalds",
            "name": "Linus Torvalds",
            "bio": "Creator of Linux and Git",
            "location": "Portland, OR",
            "email": None,
            "followers": 200000,
            "created_at": "2011-09-03T15:26:22Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/1024025",
            "html_url": "https://github.com/torvalds"
        }
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = GitHubClient(token="fake_token")
            profile = await client.get_profile("torvalds")

            assert profile["login"] == "torvalds"
            assert profile["name"] == "Linus Torvalds"
            assert profile["followers"] == 200000

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_github_client_get_repos():
    """get_repos should fetch user repositories."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        mock_response = MagicMock()
        mock_response.status_code = 200
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
                "name": "test-repo",
                "description": "Test repository",
                "stargazers_count": 10,
                "forks_count": 2,
                "language": "Shell",
                "html_url": "https://github.com/torvalds/test-repo"
            }
        ]
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890"
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = GitHubClient(token="fake_token")
            repos = await client.get_repos("torvalds")

            assert len(repos) == 2
            assert repos[0]["name"] == "linux"
            assert repos[0]["stargazers_count"] == 150000

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_get_profile_404_returns_none():
    """get_profile for non-existent user should return None."""
    try:
        from src.github_sourcer.services.github_client import GitHubClient

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = GitHubClient(token="fake_token")
            profile = await client.get_profile("nonexistentuser123456")

            assert profile is None

    except ImportError as e:
        pytest.fail(f"GitHubClient not implemented yet: {e}")


@pytest.mark.asyncio
async def test_profile_enricher_creates_candidate():
    """ProfileEnricher should combine user + repos into Candidate."""
    try:
        from src.github_sourcer.services.profile_enricher import ProfileEnricher
        from src.github_sourcer.services.github_client import GitHubClient

        # Mock GitHub client
        mock_client = MagicMock(spec=GitHubClient)
        mock_client.get_profile = AsyncMock(return_value={
            "login": "testuser",
            "name": "Test User",
            "bio": "Software developer",
            "location": "San Francisco",
            "email": None,
            "followers": 100,
            "created_at": "2020-01-01T00:00:00Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/12345",
            "html_url": "https://github.com/testuser"
        })
        mock_client.get_repos = AsyncMock(return_value=[
            {
                "name": "awesome-project",
                "description": "An awesome project",
                "stargazers_count": 500,
                "forks_count": 50,
                "language": "Python",
                "html_url": "https://github.com/testuser/awesome-project"
            },
            {
                "name": "another-repo",
                "description": "Another repository",
                "stargazers_count": 20,
                "forks_count": 5,
                "language": "JavaScript",
                "html_url": "https://github.com/testuser/another-repo"
            }
        ])

        enricher = ProfileEnricher(github_client=mock_client)
        candidate = await enricher.enrich_profile("testuser")

        assert candidate.github_username == "testuser"
        assert candidate.name == "Test User"
        assert candidate.followers == 100
        assert len(candidate.top_repos) == 2
        assert "Python" in candidate.languages

    except ImportError as e:
        pytest.fail(f"ProfileEnricher not implemented yet: {e}")


@pytest.mark.asyncio
async def test_profile_enricher_handles_no_repos():
    """ProfileEnricher should handle users with no repositories."""
    try:
        from src.github_sourcer.services.profile_enricher import ProfileEnricher
        from src.github_sourcer.services.github_client import GitHubClient

        mock_client = MagicMock(spec=GitHubClient)
        mock_client.get_profile = AsyncMock(return_value={
            "login": "newuser",
            "name": "New User",
            "bio": None,
            "location": None,
            "email": None,
            "followers": 0,
            "created_at": "2025-01-01T00:00:00Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/99999",
            "html_url": "https://github.com/newuser"
        })
        mock_client.get_repos = AsyncMock(return_value=[])  # No repos

        enricher = ProfileEnricher(github_client=mock_client)
        candidate = await enricher.enrich_profile("newuser")

        assert candidate.github_username == "newuser"
        assert candidate.top_repos == []
        assert candidate.languages == []

    except ImportError as e:
        pytest.fail(f"ProfileEnricher not implemented yet: {e}")


@pytest.mark.asyncio
async def test_profile_enricher_404_raises_exception():
    """ProfileEnricher should raise exception for non-existent users."""
    try:
        from src.github_sourcer.services.profile_enricher import ProfileEnricher
        from src.github_sourcer.services.github_client import GitHubClient

        mock_client = MagicMock(spec=GitHubClient)
        mock_client.get_profile = AsyncMock(return_value=None)  # 404

        enricher = ProfileEnricher(github_client=mock_client)

        with pytest.raises(Exception):  # Should raise ProfileNotFoundError or similar
            await enricher.enrich_profile("nonexistentuser")

    except ImportError as e:
        pytest.fail(f"ProfileEnricher not implemented yet: {e}")
