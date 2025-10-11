"""Contract tests for database initialization and connection."""

import pytest
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.backend_api.database import init_db, get_db
from src.backend_api.models import Base, User, Project, Session


@pytest.fixture
async def test_engine():
    """Create a test database engine (in-memory SQLite)."""
    # Use in-memory database for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


class TestDatabaseInitialization:
    """Test database initialization."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, test_engine):
        """Test that init_db creates all tables."""
        # Tables should already be created by fixture
        # Verify by trying to query them
        async with AsyncSession(test_engine) as session:
            # Should not raise any errors
            result = await session.execute(select(User))
            assert result.scalars().all() == []

            result = await session.execute(select(Project))
            assert result.scalars().all() == []

            result = await session.execute(select(Session))
            assert result.scalars().all() == []

    @pytest.mark.asyncio
    async def test_database_session_creation(self, test_session):
        """Test creating and using a database session."""
        # Create a user
        user = User(
            email="test@example.com",
            hashed_password="hashed_pass"
        )

        test_session.add(user)
        await test_session.commit()

        # Query the user
        result = await test_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        fetched_user = result.scalars().first()

        assert fetched_user is not None
        assert fetched_user.email == "test@example.com"
        assert fetched_user.hashed_password == "hashed_pass"

    @pytest.mark.asyncio
    async def test_user_project_relationship(self, test_session):
        """Test User-Project relationship."""
        # Create user
        user = User(
            email="test@example.com",
            hashed_password="hash"
        )
        test_session.add(user)
        await test_session.commit()

        # Create project for user
        project = Project(
            user_id=user.user_id,
            job_description_text="Test JD"
        )
        test_session.add(project)
        await test_session.commit()

        # Refresh user to load relationships
        await test_session.refresh(user, attribute_names=['projects'])

        # Verify relationship
        assert len(user.projects) == 1
        assert user.projects[0].project_id == project.project_id
