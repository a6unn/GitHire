"""End-to-end integration tests for complete user journeys."""

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


class TestFullUserJourney:
    """Test complete user journey from registration to project management."""

    @pytest.mark.asyncio
    async def test_complete_recruitment_workflow(self, override_get_db):
        """Test full workflow: register → login → run pipeline → view project → export → delete."""
        from datetime import datetime

        # Mock pipeline execution
        start_time = datetime(2025, 10, 6, 12, 0, 0)
        end_time = datetime(2025, 10, 6, 12, 0, 10)

        mock_result = {
            "status": "success",
            "job_requirement": {
                "original_input": "Looking for Senior Python Developer",
                "role": "Senior Python Developer",
                "required_skills": ["Python", "FastAPI", "SQLAlchemy"],
                "experience_years": 5,
                "seniority_level": "senior",
            },
            "candidates": [
                {
                    "github_username": "pythondev1",
                    "profile_url": "https://github.com/pythondev1",
                    "repositories": ["fastapi-app", "sqlalchemy-tutorial"],
                    "programming_languages": ["Python"],
                    "location": "San Francisco",
                    "bio": "Python developer",
                    "contribution_count": 500,
                    "account_age_days": 1000,
                }
            ],
            "ranked_candidates": [
                {
                    "github_username": "pythondev1",
                    "total_score": 85.5,
                    "rank": 1,
                    "domain_score": 90.0,
                    "score_breakdown": {
                        "skill_match": 90.0,
                        "experience": 85.0,
                        "activity": 82.0
                    },
                    "strengths": ["Strong Python skills"],
                    "concerns": [],
                }
            ],
            "outreach_messages": [
                {
                    "github_username": "pythondev1",
                    "message": "Hi! We have an exciting opportunity...",
                    "personalization_notes": "Relevant FastAPI experience",
                    "subject": "Senior Python Developer Opportunity",
                }
            ],
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
                # Step 1: Register new user
                register_response = await client.post(
                    "/auth/register",
                    json={
                        "email": "recruiter@company.com",
                        "password": "securepassword123",
                    },
                )
                assert register_response.status_code == 201
                assert "user_id" in register_response.json()

                # Step 2: Login
                login_response = await client.post(
                    "/auth/login",
                    json={
                        "email": "recruiter@company.com",
                        "password": "securepassword123",
                    },
                )
                assert login_response.status_code == 200
                token = login_response.json()["access_token"]
                assert token is not None

                headers = {"Authorization": f"Bearer {token}"}

                # Step 3: Verify no projects exist initially
                list_response = await client.get("/projects", headers=headers)
                assert list_response.status_code == 200
                assert list_response.json()["total"] == 0

                # Step 4: Run recruitment pipeline
                run_response = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for Senior Python Developer with 5+ years experience"},
                    headers=headers,
                )
                assert run_response.status_code == 200
                run_data = run_response.json()
                project_id = run_data["project_id"]
                assert run_data["status"] == "success"
                assert run_data["metadata"]["candidates_found"] == 1
                assert run_data["metadata"]["messages_generated"] == 1

                # Step 5: Check project list shows the new project
                list_response = await client.get("/projects", headers=headers)
                assert list_response.status_code == 200
                list_data = list_response.json()
                assert list_data["total"] == 1
                assert list_data["projects"][0]["project_id"] == project_id
                assert list_data["projects"][0]["status"] == "completed"

                # Step 6: Get detailed project information
                detail_response = await client.get(f"/projects/{project_id}", headers=headers)
                assert detail_response.status_code == 200
                detail_data = detail_response.json()
                assert detail_data["project_id"] == project_id
                assert detail_data["candidate_count"] == 1
                assert detail_data["results_json"] is not None

                # Step 7: Export project results
                export_response = await client.get(f"/projects/{project_id}/export", headers=headers)
                assert export_response.status_code == 200
                assert "application/json" in export_response.headers["content-type"]
                assert "attachment" in export_response.headers.get("content-disposition", "")
                export_data = export_response.json()
                assert export_data["status"] == "success"
                assert export_data["candidates"][0]["github_username"] == "pythondev1"

                # Step 8: Check pipeline status
                status_response = await client.get(f"/pipeline/status/{project_id}", headers=headers)
                assert status_response.status_code == 200
                status_data = status_response.json()
                assert status_data["status"] == "completed"
                assert status_data["progress_percentage"] == 100

                # Step 9: Delete project
                delete_response = await client.delete(f"/projects/{project_id}", headers=headers)
                assert delete_response.status_code == 200
                assert "deleted" in delete_response.json()["message"].lower()

                # Step 10: Verify project is deleted
                get_deleted_response = await client.get(f"/projects/{project_id}", headers=headers)
                assert get_deleted_response.status_code == 404

                # Step 11: Verify project list is empty again
                final_list_response = await client.get("/projects", headers=headers)
                assert final_list_response.status_code == 200
                assert final_list_response.json()["total"] == 0

                # Step 12: Logout
                logout_response = await client.post("/auth/logout", headers=headers)
                assert logout_response.status_code == 200


class TestMultipleUsers:
    """Test multiple users with isolated data."""

    @pytest.mark.asyncio
    async def test_multiple_users_data_isolation(self, override_get_db):
        """Test that multiple users can work independently with isolated data."""
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
                # User 1: Register and login
                await client.post(
                    "/auth/register",
                    json={"email": "user1@company.com", "password": "password123"},
                )
                login1 = await client.post(
                    "/auth/login",
                    json={"email": "user1@company.com", "password": "password123"},
                )
                token1 = login1.json()["access_token"]

                # User 2: Register and login
                await client.post(
                    "/auth/register",
                    json={"email": "user2@company.com", "password": "password456"},
                )
                login2 = await client.post(
                    "/auth/login",
                    json={"email": "user2@company.com", "password": "password456"},
                )
                token2 = login2.json()["access_token"]

                # User 1 creates a project
                run1 = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for Python Developer"},
                    headers={"Authorization": f"Bearer {token1}"},
                )
                project1_id = run1.json()["project_id"]

                # User 2 creates a project
                run2 = await client.post(
                    "/pipeline/run",
                    json={"job_description_text": "Looking for JavaScript Developer"},
                    headers={"Authorization": f"Bearer {token2}"},
                )
                project2_id = run2.json()["project_id"]

                # User 1 should only see their project
                list1 = await client.get(
                    "/projects",
                    headers={"Authorization": f"Bearer {token1}"},
                )
                assert list1.status_code == 200
                assert list1.json()["total"] == 1
                assert list1.json()["projects"][0]["project_id"] == project1_id

                # User 2 should only see their project
                list2 = await client.get(
                    "/projects",
                    headers={"Authorization": f"Bearer {token2}"},
                )
                assert list2.status_code == 200
                assert list2.json()["total"] == 1
                assert list2.json()["projects"][0]["project_id"] == project2_id

                # User 1 cannot access User 2's project
                forbidden1 = await client.get(
                    f"/projects/{project2_id}",
                    headers={"Authorization": f"Bearer {token1}"},
                )
                assert forbidden1.status_code == 403

                # User 2 cannot access User 1's project
                forbidden2 = await client.get(
                    f"/projects/{project1_id}",
                    headers={"Authorization": f"Bearer {token2}"},
                )
                assert forbidden2.status_code == 403
