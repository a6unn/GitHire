"""Database connection and session management."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

# Database configuration
# Check if running in production (Railway, Render, Vercel, etc.)
IS_PRODUCTION = any([
    os.getenv("RAILWAY_ENVIRONMENT"),
    os.getenv("RAILWAY_PROJECT_ID"),
    os.getenv("RENDER"),
    os.getenv("PORT"),  # Railway and Render set this
    os.getenv("VERCEL"),
])

# Database URL priority:
# 1. If DATABASE_URL is explicitly set → use it (PostgreSQL on Render/Railway)
# 2. If in production with no DATABASE_URL → use in-memory SQLite (ephemeral filesystem)
# 3. If in development → use file-based SQLite
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # No explicit DATABASE_URL - use SQLite
    DEFAULT_DB = "sqlite+aiosqlite:///:memory:" if IS_PRODUCTION else "sqlite+aiosqlite:///./githire.db"
    DATABASE_URL = DEFAULT_DB
else:
    # Convert postgres:// to postgresql:// for SQLAlchemy (some services use old format)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Determine database type
IS_SQLITE = "sqlite" in DATABASE_URL
IS_POSTGRES = "postgresql" in DATABASE_URL

# Log database configuration on startup
import logging
logger = logging.getLogger(__name__)
db_type = "SQLite" if IS_SQLITE else ("PostgreSQL" if IS_POSTGRES else "Unknown")
logger.info(f"Database configuration: Type={db_type}, IS_PRODUCTION={IS_PRODUCTION}")
logger.info(f"Connection: {DATABASE_URL.split('://')[0]}://{'***' if '@' in DATABASE_URL else DATABASE_URL.split('://')[1].split('/')[0]}")

# Create async engine with appropriate configuration
engine_kwargs = {
    "echo": False,  # Set to True for SQL query logging
}

# SQLite-specific configuration
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool

# PostgreSQL-specific configuration
if IS_POSTGRES:
    engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session that automatically commits/rolls back
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
