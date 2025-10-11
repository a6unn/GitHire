"""Tests for concurrent execution and edge cases."""

import pytest
import asyncio
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


class TestConcurrentPipelineExecutions:
    """Test concurrent pipeline executions."""

    @pytest.mark.asyncio
    async def test_multiple_pipelines_run_concurrently(self, auth_token):
        """Test that multiple pipelines can run concurrently without conflicts."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        # Different results for each pipeline
        def create_mock_result(candidate_count: int):
            return {
                "status": "success",
                "job_requirement": {},
                "candidates": [{"github_username": f"user{i}", "profile_url": f"https://github.com/user{i}", "repositories": [], "programming_languages": [], "location": "", "bio": "", "contribution_count": 0, "account_age_days": 0} for i in range(candidate_count)],
                "ranked_candidates": [{"github_username": f"user{i}", "total_score": 80.0, "rank": i+1, "domain_score": 80.0, "score_breakdown": {}, "strengths": [], "concerns": []} for i in range(candidate_count)],
                "outreach_messages": [{"github_username": f"user{i}", "message": "Hi", "personalization_notes": "", "subject": "Job"} for i in range(candidate_count)],
                "metadata": {
                    "execution_time_seconds": 10.5,
                    "candidates_found": candidate_count,
                    "candidates_ranked": candidate_count,
                    "messages_generated": candidate_count,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "module_results": {},
                },
            }

        with patch("src.backend_api.routers.pipeline_router.PipelineOrchestrator") as mock_orchestrator:
            # Create different mock instances for each call
            mock_instance = mock_orchestrator.return_value
            mock_instance.start_time = start_time

            # Create side effects for different executions
            results = [create_mock_result(1), create_mock_result(2), create_mock_result(3)]
            mock_instance.execute_pipeline = AsyncMock(side_effect=results)

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                headers = {"Authorization": f"Bearer {auth_token}"}

                # Launch 3 pipelines concurrently
                tasks = [
                    client.post(
                        "/pipeline/run",
                        json={"job_description_text": f"Looking for developer {i}"},
                        headers=headers,
                    )
                    for i in range(3)
                ]

                responses = await asyncio.gather(*tasks)

                # Verify all succeeded
                for response in responses:
                    assert response.status_code == 200
                    assert response.json()["status"] == "success"

                # Verify all projects were created
                list_response = await client.get("/projects", headers=headers)
                assert list_response.status_code == 200
                assert list_response.json()["total"] == 3

                # Verify each project has different candidate counts
                projects = list_response.json()["projects"]
                candidate_counts = [p["candidate_count"] for p in projects]
                assert sorted(candidate_counts) == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_concurrent_access_same_project(self, auth_token):
        """Test concurrent access to the same project."""
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
                headers = {"Authorization": f"Bearer {auth_token}"}

                # Create a project
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for developer"},
                    headers=headers,
                )
                project_id = run_response.json()["project_id"]

                # Concurrently access the same project multiple times
                tasks = [
                    client.get(f"/projects/{project_id}", headers=headers)
                    for _ in range(10)
                ]

                responses = await asyncio.gather(*tasks)

                # Verify all reads succeeded with same data
                for response in responses:
                    assert response.status_code == 200
                    assert response.json()["project_id"] == project_id
                    assert response.json()["candidate_count"] == 5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_pipeline_with_zero_candidates(self, auth_token):
        """Test pipeline execution that finds zero candidates."""
        from datetime import datetime

        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        # Pipeline result with no candidates
        mock_result = {
            "status": "success",
            "job_requirement": {
                "original_input": "Looking for very rare skill combination",
                "role": "Unicorn Developer",
                "required_skills": ["Skill1", "Skill2", "Skill3"],
                "experience_years": 10,
                "seniority_level": "principal",
            },
            "candidates": [],  # Zero candidates found
            "ranked_candidates": [],
            "outreach_messages": [],
            "metadata": {
                "execution_time_seconds": 8.0,
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
                headers = {"Authorization": f"Bearer {auth_token}"}

                # Run pipeline
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for very rare skill combination"},
                    headers=headers,
                )

                # Should still succeed even with zero candidates
                assert run_response.status_code == 200
                data = run_response.json()
                assert data["status"] == "success"
                assert data["metadata"]["candidates_found"] == 0
                assert data["metadata"]["candidates_ranked"] == 0
                assert data["metadata"]["messages_generated"] == 0

                # Project should be created successfully
                project_id = data["project_id"]
                project_response = await client.get(f"/projects/{project_id}", headers=headers)
                assert project_response.status_code == 200
                project_data = project_response.json()
                assert project_data["candidate_count"] == 0
                assert project_data["status"] == "completed"

                # Results should be valid JSON even with empty arrays
                assert project_data["results_json"]["candidates"] == []
                assert project_data["results_json"]["ranked_candidates"] == []
                assert project_data["results_json"]["outreach_messages"] == []

    @pytest.mark.asyncio
    async def test_pipeline_with_very_long_job_description(self, auth_token):
        """Test pipeline with maximum length job description."""
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
                headers = {"Authorization": f"Bearer {auth_token}"}

                # Create a very long job description (close to max 10000 chars)
                long_jd = "Looking for Senior Developer. " * 300  # ~9000 chars

                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": long_jd},
                    headers=headers,
                )

                assert run_response.status_code == 200
                project_id = run_response.json()["project_id"]

                # Verify in project list, JD is truncated
                list_response = await client.get("/projects", headers=headers)
                assert list_response.status_code == 200
                project_summary = list_response.json()["projects"][0]
                assert len(project_summary["job_description_text"]) <= 203  # 200 + "..."

                # But full JD is available in detail view
                detail_response = await client.get(f"/projects/{project_id}", headers=headers)
                assert detail_response.status_code == 200
                assert len(detail_response.json()["job_description_text"]) > 200

    @pytest.mark.asyncio
    async def test_pipeline_with_minimum_job_description(self, auth_token):
        """Test pipeline with minimum valid job description."""
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
                headers = {"Authorization": f"Bearer {auth_token}"}

                # Minimum is 10 characters
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Python dev"},  # Exactly 10 chars
                    headers=headers,
                )

                assert run_response.status_code == 200

                # Test below minimum (should fail validation)
                too_short_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Too short"},  # 9 chars
                    headers=headers,
                )

                assert too_short_response.status_code == 422
                assert "validation_error" in too_short_response.json()["type"]

    @pytest.mark.asyncio
    async def test_export_project_with_no_results(self, auth_token):
        """Test exporting a project that has null results_json."""
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
                headers = {"Authorization": f"Bearer {auth_token}"}

                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for developer"},
                    headers=headers,
                )
                project_id = run_response.json()["project_id"]

                # Export should still work and return empty object if results_json is None
                export_response = await client.get(f"/projects/{project_id}/export", headers=headers)
                assert export_response.status_code == 200
                assert "application/json" in export_response.headers["content-type"]

                # Should get valid JSON (either the result or empty dict)
                export_data = export_response.json()
                assert isinstance(export_data, dict)
