"""API tests for pipeline router endpoints."""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.backend_api.main import app
from src.backend_api.models import Base
from src.backend_api.database import get_db


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


class TestPipelineRun:
    """Test /pipeline/run endpoint."""

    @pytest.mark.asyncio
    async def test_run_pipeline_success(self, auth_token):
        """Test successful pipeline execution."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        mock_result = {
            "status": "success",
            "job_requirement": {"role": "Senior Python Developer"},
            "candidates": [{"github_username": "dev1"}],
            "ranked_candidates": [{"rank": 1}],
            "outreach_messages": [{"candidate_username": "dev1"}],
            "metadata": {
                "execution_time_seconds": 10.5,
                "candidates_found": 1,
                "candidates_ranked": 1,
                "messages_generated": 1,
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
                response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for Senior Python Developer"},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert "project_id" in data
            assert data["status"] == "success"
            assert "candidates" in data
            assert "ranked_candidates" in data
            assert "outreach_messages" in data
            assert "metadata" in data

    @pytest.mark.asyncio
    async def test_run_pipeline_requires_authentication(self, override_get_db):
        """Test that pipeline run requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/pipeline/run",
                json={"job_description_text": "Looking for developer"},
            )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_run_pipeline_invalid_job_description(self, auth_token):
        """Test pipeline run with invalid job description."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/pipeline/run",
                json={"job_description_text": "short"},  # Too short (min 10 chars)
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_run_pipeline_execution_failure(self, auth_token):
        """Test pipeline execution failure."""
        from src.backend_api.pipeline import PipelineException

        with patch("src.backend_api.routers.pipeline_router.PipelineOrchestrator") as mock_orchestrator:
            mock_instance = mock_orchestrator.return_value
            mock_instance.execute_pipeline = AsyncMock(
                side_effect=PipelineException("Test failure", "Module 001")
            )

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for Senior Python Developer"},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

            assert response.status_code == 400
            assert "Pipeline execution failed" in response.json()["detail"]


class TestPipelineStatus:
    """Test /pipeline/status/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_status_completed_pipeline(self, auth_token):
        """Test getting status for completed pipeline."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        # First run a pipeline to create a project
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
                # Run pipeline
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for developer"},
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

                project_id = run_response.json()["project_id"]

                # Get status
                status_response = await client.get(
                    f"/pipeline/status/{project_id}",
                    headers={"Authorization": f"Bearer {auth_token}"},
                )

            assert status_response.status_code == 200
            data = status_response.json()
            assert data["project_id"] == project_id
            assert data["status"] == "completed"
            assert data["progress_percentage"] == 100

    @pytest.mark.asyncio
    async def test_get_status_nonexistent_project(self, auth_token):
        """Test getting status for non-existent project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/pipeline/status/nonexistent-id",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_status_unauthorized_access(self, auth_token):
        """Test unauthorized access to project status."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        # Create a project with one user
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

                # Register a second user
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
                status_response = await client.get(
                    f"/pipeline/status/{project_id}",
                    headers={"Authorization": f"Bearer {other_token}"},
                )

            assert status_response.status_code == 403
            assert "not authorized" in status_response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_status_requires_authentication(self, override_get_db):
        """Test that status endpoint requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/pipeline/status/some-id")

        assert response.status_code == 403
