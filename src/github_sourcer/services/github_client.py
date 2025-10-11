"""GitHub API client for searching users and fetching profiles.

Handles authentication, rate limiting, and error handling.
"""

import httpx
import logging
from typing import Optional, Dict, List
from src.github_sourcer.lib.rate_limiter import RateLimiter, RateLimitExceeded
from src.github_sourcer.config import Config

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Raised when GitHub API returns an error."""
    pass


class GitHubClient:
    """Async HTTP client for GitHub API."""

    def __init__(self, token: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize GitHub API client.

        Args:
            token: GitHub Personal Access Token (defaults to Config.GITHUB_TOKEN)
            timeout: HTTP request timeout in seconds (default: 30.0)
        """
        self.token = token or Config.GITHUB_TOKEN
        self.base_url = Config.GITHUB_API_BASE
        self.timeout = timeout
        self.rate_limiter = RateLimiter(threshold=Config.RATE_LIMIT_THRESHOLD)
        self.client = httpx.AsyncClient(timeout=self.timeout, headers=self._get_headers())
        self._closed = False

        if not self.token:
            logger.warning("No GitHub token provided - API calls will be rate limited to 60/hour")

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHire-Sourcer/1.0"
        }

        if self.token:
            headers["Authorization"] = f"token {self.token}"

        return headers

    async def search_users(self, query: str, per_page: int = 30, max_results: Optional[int] = None) -> List[str]:
        """
        Search GitHub users.

        Args:
            query: GitHub search query (e.g., "language:python location:india")
            per_page: Results per page (default: 30, max: 100)
            max_results: Maximum total results to return (optional)

        Returns:
            List of GitHub usernames

        Raises:
            ValueError: If query is empty
            GitHubAPIError: If rate limit is exceeded
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        url = f"{self.base_url}/search/users"
        params = {
            "q": query.strip(),
            "per_page": min(per_page, 100)  # GitHub max is 100
        }

        for attempt in range(self.rate_limiter.max_retries):
            try:
                response = await self.client.get(url, params=params)

                # Check rate limit
                try:
                    self.rate_limiter.check_quota(dict(response.headers))
                except RateLimitExceeded as e:
                    # Wrap RateLimitExceeded in GitHubAPIError
                    raise GitHubAPIError(f"Rate limit exceeded: {e}")

                if response.status_code == 403:
                    # Rate limit exceeded
                    await self.rate_limiter.handle_rate_limit_error(attempt)
                    continue  # Retry

                if response.status_code == 200:
                    data = response.json()
                    usernames = [item["login"] for item in data.get("items", [])]

                    # Limit results if max_results specified
                    if max_results and len(usernames) > max_results:
                        usernames = usernames[:max_results]

                    logger.info(f"Found {len(usernames)} users for query: {query}")
                    return usernames

                # Other errors
                logger.error(f"GitHub search failed: {response.status_code} - {response.text}")
                raise GitHubAPIError(f"GitHub API error: {response.status_code}")

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during search: {e}")
                if attempt == self.rate_limiter.max_retries - 1:
                    raise GitHubAPIError(f"HTTP error after {attempt + 1} retries: {e}")
                await self.rate_limiter.handle_rate_limit_error(attempt)

        # Max retries exceeded
        raise GitHubAPIError(f"Max retries exceeded for search query: {query}")

    async def get_profile(self, username: str) -> Optional[Dict]:
        """
        Fetch user profile data.

        Args:
            username: GitHub username

        Returns:
            User profile dict or None if not found
        """
        url = f"{self.base_url}/users/{username}"

        try:
            response = await self.client.get(url)

            # Check rate limit
            self.rate_limiter.check_quota(dict(response.headers))

            if response.status_code == 404:
                logger.warning(f"Profile not found: {username}")
                return None

            if response.status_code == 200:
                return response.json()

            logger.error(f"Failed to fetch profile for {username}: {response.status_code}")
            return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching profile for {username}: {e}")
            return None

    async def get_repos(self, username: str, per_page: int = 100) -> List[Dict]:
        """
        Fetch user repositories.

        Args:
            username: GitHub username
            per_page: Results per page (default: 100)

        Returns:
            List of repository dicts
        """
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            "per_page": per_page,
            "sort": "stars",  # Sort by stars
            "direction": "desc"
        }

        try:
            response = await self.client.get(url, params=params)

            # Check rate limit
            self.rate_limiter.check_quota(dict(response.headers))

            if response.status_code == 200:
                repos = response.json()
                logger.debug(f"Found {len(repos)} repos for {username}")
                return repos

            logger.error(f"Failed to fetch repos for {username}: {response.status_code}")
            return []

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching repos for {username}: {e}")
            return []

    async def close(self):
        """Close the HTTP client connection."""
        if self.client and not self._closed:
            await self.client.aclose()
            self.client = None
            self._closed = True
            logger.debug("GitHubClient connection closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False

    async def batch_get_profiles_graphql(self, usernames: List[str]) -> List[Dict]:
        """
        Fetch multiple user profiles using GraphQL batching (4.6x faster).

        Args:
            usernames: List of GitHub usernames to fetch

        Returns:
            List of user profile dicts

        Raises:
            GitHubAPIError: If GraphQL query fails
        """
        if not usernames:
            return []

        # Build GraphQL query for batch fetching
        # Example: query { user0: user(login:"user1") { login name ... } }
        query_parts = []
        for idx, username in enumerate(usernames[:50]):  # Max 50 per batch
            query_parts.append(f'''
            user{idx}: user(login: "{username}") {{
                login
                name
                bio
                location
                email
                publicRepositories: repositories(first: 0) {{ totalCount }}
                followers {{ totalCount }}
                createdAt
                avatarUrl
                url
            }}
        ''')

        graphql_query = "query { " + " ".join(query_parts) + " }"

        url = "https://api.github.com/graphql"
        payload = {"query": graphql_query}

        try:
            response = await self.client.post(url, json=payload)
            self.rate_limiter.check_quota(dict(response.headers))

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    raise GitHubAPIError(f"GraphQL errors: {data['errors']}")

                # Extract profiles from response
                profiles = []
                for key, profile in data.get("data", {}).items():
                    if profile:  # Skip null users (not found)
                        profiles.append(profile)

                logger.info(f"Fetched {len(profiles)} profiles via GraphQL batch")
                return profiles
            else:
                raise GitHubAPIError(f"GraphQL request failed: {response.status_code}")

        except httpx.HTTPError as e:
            raise GitHubAPIError(f"HTTP error during GraphQL batch: {e}")

    async def get_dependency_graph(self, username: str, repo: str) -> Optional[Dict]:
        """
        Fetch dependency graph for a repository (for skills detection).

        Args:
            username: Repository owner username
            repo: Repository name

        Returns:
            Dependency graph dict or None if not available

        Note:
            This uses GitHub's Dependency Graph API which may not be available for all repos.
            Requires appropriate token permissions.
        """
        # GitHub Dependency Graph API endpoint
        # Note: This is a preview API and may require special headers
        url = f"{self.base_url}/repos/{username}/{repo}/dependency-graph/sbom"

        headers = self._get_headers()
        headers["Accept"] = "application/vnd.github.dependency-graph-preview+json"

        try:
            response = await self.client.get(url, headers=headers)
            self.rate_limiter.check_quota(dict(response.headers))

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.debug(f"Dependency graph not available for {username}/{repo}")
                return None
            else:
                logger.warning(f"Failed to fetch dependency graph: {response.status_code}")
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching dependency graph: {e}")
            return None
