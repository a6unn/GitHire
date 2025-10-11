"""API tests for projects router endpoints."""

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


@pytest.fixture
async def sample_project(auth_token):
    """Create a sample project for testing."""
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
            "candidates_found": 5,
            "candidates_ranked": 5,
            "messages_generated": 5,
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
                json={"job_description_text": "Looking for Senior Python Developer with 5+ years experience"},
                headers={"Authorization": f"Bearer {auth_token}"},
            )

            return response.json()["project_id"]


class TestListProjects:
    """Test GET /projects endpoint."""

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, auth_token):
        """Test listing projects when user has none."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/projects",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["projects"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_projects_with_data(self, auth_token, sample_project):
        """Test listing projects when user has projects."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/projects",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 1
        assert data["total"] == 1

        project = data["projects"][0]
        assert project["project_id"] == sample_project
        assert project["status"] == "completed"
        assert project["candidate_count"] == 5
        assert "job_description_text" in project
        assert len(project["job_description_text"]) <= 203  # 200 chars + "..."

    @pytest.mark.asyncio
    async def test_list_projects_requires_authentication(self, override_get_db):
        """Test that listing projects requires authentication."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/projects")

        assert response.status_code == 403


class TestGetProject:
    """Test GET /projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_project_success(self, auth_token, sample_project):
        """Test getting project details."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/projects/{sample_project}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == sample_project
        assert data["status"] == "completed"
        assert data["candidate_count"] == 5
        assert "job_description_text" in data
        assert "results_json" in data
        assert data["results_json"] is not None

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, auth_token):
        """Test getting non-existent project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/projects/nonexistent-id",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_project_unauthorized(self, auth_token, sample_project):
        """Test unauthorized access to another user's project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
                f"/projects/{sample_project}",
                headers={"Authorization": f"Bearer {other_token}"},
            )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()


class TestDeleteProject:
    """Test DELETE /projects/{project_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, auth_token, sample_project):
        """Test deleting project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Delete project
            response = await client.delete(
                f"/projects/{sample_project}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify project is deleted
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            get_response = await client.get(
                f"/projects/{sample_project}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, auth_token):
        """Test deleting non-existent project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(
                "/projects/nonexistent-id",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_unauthorized(self, auth_token, sample_project):
        """Test unauthorized deletion of another user's project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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

            # Try to delete first user's project
            response = await client.delete(
                f"/projects/{sample_project}",
                headers={"Authorization": f"Bearer {other_token}"},
            )

        assert response.status_code == 403


class TestExportProject:
    """Test GET /projects/{project_id}/export endpoint."""

    @pytest.mark.asyncio
    async def test_export_project_success(self, auth_token, sample_project):
        """Test exporting project as JSON."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/projects/{sample_project}/export",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        assert "attachment" in response.headers.get("content-disposition", "")

        # Verify it's valid JSON
        data = response.json()
        assert "status" in data
        assert "metadata" in data

    @pytest.mark.asyncio
    async def test_export_project_not_found(self, auth_token):
        """Test exporting non-existent project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/projects/nonexistent-id/export",
                headers={"Authorization": f"Bearer {auth_token}"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_project_unauthorized(self, auth_token, sample_project):
        """Test unauthorized export of another user's project."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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

            # Try to export first user's project
            response = await client.get(
                f"/projects/{sample_project}/export",
                headers={"Authorization": f"Bearer {other_token}"},
            )

        assert response.status_code == 403
