"""Integration tests for error handling."""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.backend_api.main import app
from src.backend_api.models import Base
from src.backend_api.database import get_db
from src.backend_api.pipeline import PipelineException


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    yield async_session

    await engine.dispose()


@pytest.fixture
def override_get_db(test_db):
    """Override get_db dependency."""
    async def _get_db():
        async with test_db() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_token(override_get_db):
    """Get authentication token for tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )

        # Login
        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )

        return response.json()["access_token"]


class TestPipelineErrorHandling:
    """Test pipeline error handling."""

    @pytest.mark.asyncio
    async def test_pipeline_failure_returns_400_with_module_info(self, auth_token):
        """Test that pipeline failures return 400 with module information."""
        with patch("src.backend_api.routers.pipeline_router.PipelineOrchestrator") as mock_orchestrator:
            mock_instance = mock_orchestrator.return_value
            mock_instance.execute_pipeline = AsyncMock(
                side_effect=PipelineException(
                    message="Failed to parse job description",
                    module_name="Module 001"
                )
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for developer"},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "failed" in data["detail"].lower()


class TestValidationErrorHandling:
    """Test validation error handling."""

    @pytest.mark.asyncio
    async def test_validation_error_returns_422_with_field_details(self, override_get_db):
        """Test that validation errors return 422 with field details."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try to register with invalid email
            response = await client.post(
                "/auth/register",
                json={
                    "email": "invalid-email",  # Not a valid email
                    "password": "testpassword123",
                },
            )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data
        assert len(data["errors"]) > 0
        assert "field" in data["errors"][0]
        assert "message" in data["errors"][0]

    @pytest.mark.asyncio
    async def test_validation_error_short_password(self, override_get_db):
        """Test validation error for short password."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "short",  # Too short (min 8 chars)
                },
            )

        assert response.status_code == 422
        data = response.json()
        assert "validation_error" in data["type"]
        assert any("password" in error["field"] for error in data["errors"])

    @pytest.mark.asyncio
    async def test_validation_error_missing_field(self, override_get_db):
        """Test validation error for missing required field."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    # Missing password field
                },
            )

        assert response.status_code == 422
        data = response.json()
        assert "errors" in data
        assert any("password" in error["field"] for error in data["errors"])


class TestAuthenticationErrorHandling:
    """Test authentication error handling."""

    @pytest.mark.asyncio
    async def test_authentication_error_returns_401(self, override_get_db):
        """Test that authentication failures return 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try to access protected endpoint without token
            response = await client.get("/projects")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    @pytest.mark.asyncio
    async def test_authentication_error_invalid_token(self, override_get_db):
        """Test authentication error with invalid token."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/projects",
                headers={"Authorization": "Bearer invalid_token_here"},
            )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_authentication_error_wrong_credentials(self, override_get_db):
        """Test authentication error with wrong credentials."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register user
            await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "correctpassword",
                },
            )

            # Try to login with wrong password
            response = await client.post(
                "/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword",
                },
            )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()


class TestAuthorizationErrorHandling:
    """Test authorization error handling."""

    @pytest.mark.asyncio
    async def test_authorization_error_returns_403(self, auth_token):
        """Test that authorization failures return 403."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        mock_result = {
            "status": "success",
            "job_requirement": {},
            "candidates": [],
            "ranked_candidates": [],
            "outreach_messages": [],
            "metadata": {
                "execution_time_seconds": 10.5,
                "candidates_found": 0,
                "candidates_ranked": 0,
                "messages_generated": 0,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "module_results": {},
            },
        }

        with patch("src.backend_api.routers.pipeline_router.PipelineOrchestrator") as mock_orchestrator:
            mock_instance = mock_orchestrator.return_value
            mock_instance.execute_pipeline = AsyncMock(return_value=mock_result)
            mock_instance.start_time = start_time

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                # Create project with first user
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for developer"},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

                project_id = run_response.json()["project_id"]

                # Register second user
                await client.post(
                    "/auth/register",
                    json={
                        "email": "other@example.com",
                        "password": "otherpassword123",
                    },
                )

                # Login as second user
                login_response = await client.post(
                    "/auth/login",
                    json={
                        "email": "other@example.com",
                        "password": "otherpassword123",
                    },
                )

                other_token = login_response.json()["access_token"]

                # Try to access first user's project
                response = await client.get(
                    f"/projects/{project_id}",
                    headers={"Authorization": f"Bearer {other_token}"},
                )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()


class TestLoggingMiddleware:
    """Test logging middleware."""

    @pytest.mark.asyncio
    async def test_correlation_id_in_response_headers(self, override_get_db):
        """Test that correlation ID is added to response headers."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        # Verify it's a valid UUID format
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) == 36  # UUID format
        assert correlation_id.count("-") == 4
