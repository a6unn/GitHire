"""Contract tests for FastAPI application."""

import pytest
from httpx import AsyncClient, ASGITransport

from src.backend_api.main import app


class TestFastAPIApp:
    """Test FastAPI application setup."""

    @pytest.mark.asyncio
    async def test_app_health_check(self):
        """Test /health endpoint returns healthy status."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    @pytest.mark.asyncio
    async def test_app_root_endpoint(self):
        """Test root endpoint returns welcome message."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "health" in data
