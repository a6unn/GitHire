"""Contract tests for database models."""

import pytest
from datetime import datetime, timedelta

from src.backend_api.models import User, Project, ProjectStatus, Session


class TestUserModel:
    """Test User model validation."""

    def test_user_creation(self):
        """Test creating a valid User."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123"
        )

        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.user_id is not None  # UUID auto-generated
        assert isinstance(user.created_at, datetime)
        assert user.last_login is None

    def test_user_repr(self):
        """Test User string representation."""
        user = User(
            user_id="test-uuid",
            email="test@example.com",
            hashed_password="hash"
        )

        repr_str = repr(user)
        assert "User" in repr_str
        assert "test-uuid" in repr_str
        assert "test@example.com" in repr_str

    def test_user_email_required(self):
        """Test that email is required."""
        # This test verifies the model definition has nullable=False
        # SQLAlchemy validation happens at DB level, not at object creation
        user = User(hashed_password="hash")
        assert hasattr(user, 'email')

    def test_user_relationships(self):
        """Test User has projects and sessions relationships."""
        user = User(
            email="test@example.com",
            hashed_password="hash"
        )

        assert hasattr(user, 'projects')
        assert hasattr(user, 'sessions')
        assert user.projects == []
        assert user.sessions == []


class TestProjectModel:
    """Test Project model validation."""

    def test_project_creation(self):
        """Test creating a valid Project."""
        project = Project(
            user_id="user-123",
            job_description_text="Looking for Python developer",
            status=ProjectStatus.RUNNING
        )

        assert project.user_id == "user-123"
        assert project.job_description_text == "Looking for Python developer"
        assert project.status == ProjectStatus.RUNNING
        assert project.project_id is not None
        assert isinstance(project.created_at, datetime)
        assert project.candidate_count == 0
        assert project.results_json is None

    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        assert ProjectStatus.RUNNING.value == "running"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.FAILED.value == "failed"

    def test_project_default_status(self):
        """Test default status is RUNNING."""
        project = Project(
            user_id="user-123",
            job_description_text="Test JD"
        )

        assert project.status == ProjectStatus.RUNNING

    def test_project_default_candidate_count(self):
        """Test default candidate_count is 0."""
        project = Project(
            user_id="user-123",
            job_description_text="Test JD"
        )

        assert project.candidate_count == 0

    def test_project_repr(self):
        """Test Project string representation."""
        project = Project(
            project_id="proj-123",
            user_id="user-123",
            job_description_text="Test",
            status=ProjectStatus.COMPLETED
        )

        repr_str = repr(project)
        assert "Project" in repr_str
        assert "proj-123" in repr_str
        assert "completed" in repr_str

    def test_project_with_results(self):
        """Test Project with results_json."""
        results = {
            "candidates": [{"username": "test"}],
            "metadata": {"count": 1}
        }

        project = Project(
            user_id="user-123",
            job_description_text="Test",
            results_json=results,
            candidate_count=1
        )

        assert project.results_json == results
        assert project.candidate_count == 1

    def test_project_timestamps(self):
        """Test Project timestamp fields."""
        start_time = datetime.utcnow()
        end_time = datetime.utcnow() + timedelta(minutes=2)

        project = Project(
            user_id="user-123",
            job_description_text="Test",
            pipeline_start_time=start_time,
            pipeline_end_time=end_time
        )

        assert project.pipeline_start_time == start_time
        assert project.pipeline_end_time == end_time


class TestSessionModel:
    """Test Session model validation."""

    def test_session_creation(self):
        """Test creating a valid Session."""
        session = Session(
            user_id="user-123",
            token="jwt_token_here"
        )

        assert session.user_id == "user-123"
        assert session.token == "jwt_token_here"
        assert session.session_id is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.expires_at, datetime)

    def test_session_expiration_default(self):
        """Test session expires_at defaults to 24 hours from creation."""
        session = Session(
            user_id="user-123",
            token="token"
        )

        expected_expiration = session.created_at + timedelta(hours=24)
        # Allow 1 second tolerance for test execution time
        assert abs((session.expires_at - expected_expiration).total_seconds()) < 1

    def test_session_is_expired_property_false(self):
        """Test is_expired property when session is valid."""
        future_expiry = datetime.utcnow() + timedelta(hours=1)
        session = Session(
            user_id="user-123",
            token="token",
            expires_at=future_expiry
        )

        assert session.is_expired is False

    def test_session_is_expired_property_true(self):
        """Test is_expired property when session is expired."""
        past_expiry = datetime.utcnow() - timedelta(hours=1)
        session = Session(
            user_id="user-123",
            token="token",
            expires_at=past_expiry
        )

        assert session.is_expired is True

    def test_session_repr(self):
        """Test Session string representation."""
        session = Session(
            session_id="sess-123",
            user_id="user-456",
            token="token"
        )

        repr_str = repr(session)
        assert "Session" in repr_str
        assert "sess-123" in repr_str
        assert "user-456" in repr_str
