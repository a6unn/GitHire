"""Integration tests for authentication endpoints."""

import pytest
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


class TestRegistration:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, override_get_db):
        """Test successful user registration."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "test_password_123",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "user_id" in data
        assert "created_at" in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, override_get_db):
        """Test registration with duplicate email."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First registration
            await client.post(
                "/auth/register",
                json={
                    "email": "duplicate@example.com",
                    "password": "password123",
                },
            )

            # Duplicate registration
            response = await client.post(
                "/auth/register",
                json={
                    "email": "duplicate@example.com",
                    "password": "password456",
                },
            )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, override_get_db):
        """Test registration with invalid email format."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "invalid-email",
                    "password": "password123",
                },
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, override_get_db):
        """Test registration with password too short."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "short",
                },
            )

        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, override_get_db):
        """Test successful login."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register user first
            await client.post(
                "/auth/register",
                json={
                    "email": "login@example.com",
                    "password": "password123",
                },
            )

            # Login
            response = await client.post(
                "/auth/login",
                json={
                    "email": "login@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, override_get_db):
        """Test login with wrong password."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register user first
            await client.post(
                "/auth/register",
                json={
                    "email": "wrong@example.com",
                    "password": "correct_password",
                },
            )

            # Login with wrong password
            response = await client.post(
                "/auth/login",
                json={
                    "email": "wrong@example.com",
                    "password": "wrong_password",
                },
            )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, override_get_db):
        """Test login with non-existent user."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestLogout:
    """Test user logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, override_get_db):
        """Test successful logout."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register and login
            await client.post(
                "/auth/register",
                json={
                    "email": "logout@example.com",
                    "password": "password123",
                },
            )

            login_response = await client.post(
                "/auth/login",
                json={
                    "email": "logout@example.com",
                    "password": "password123",
                },
            )
            token = login_response.json()["access_token"]

            # Logout
            response = await client.post(
                "/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_without_token(self, override_get_db):
        """Test logout without authentication token."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/auth/logout")

        assert response.status_code == 403  # Forbidden (no credentials)

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, override_get_db):
        """Test logout with invalid token."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer invalid_token"},
            )

        assert response.status_code == 401  # Unauthorized


class TestProtectedRoute:
    """Test protected routes with authentication."""

    @pytest.mark.asyncio
    async def test_access_protected_route_with_valid_token(self, override_get_db):
        """Test accessing protected route with valid token."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Register and login
            await client.post(
                "/auth/register",
                json={
                    "email": "protected@example.com",
                    "password": "password123",
                },
            )

            login_response = await client.post(
                "/auth/login",
                json={
                    "email": "protected@example.com",
                    "password": "password123",
                },
            )
            token = login_response.json()["access_token"]

            # Access protected route (logout is a protected route)
            response = await client.post(
                "/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_access_protected_route_without_token(self, override_get_db):
        """Test accessing protected route without token."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/auth/logout")

        assert response.status_code == 403
