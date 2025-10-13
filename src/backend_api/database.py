"""Database connection and session management."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

# Database configuration
# Check if running in production (Railway, Vercel, etc.) by checking common env vars
IS_PRODUCTION = any([
    os.getenv("RAILWAY_ENVIRONMENT"),
    os.getenv("RAILWAY_PROJECT_ID"),
    os.getenv("PORT"),  # Railway sets this
    os.getenv("VERCEL"),
])

# Use in-memory SQLite for production deployments (ephemeral filesystem)
# For local development, use file-based SQLite
DEFAULT_DB = "sqlite+aiosqlite:///:memory:" if IS_PRODUCTION else "sqlite+aiosqlite:///./githire.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB)

# Log database configuration on startup
import logging
logger = logging.getLogger(__name__)
logger.info(f"Database configuration: IS_PRODUCTION={IS_PRODUCTION}, DATABASE_URL={DATABASE_URL.split('://')[0]}://***")

# Create async engine
# For SQLite, use StaticPool to share single connection across async tasks
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
)

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
