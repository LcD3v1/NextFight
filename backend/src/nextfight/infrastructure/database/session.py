"""SQLAlchemy engine and session construction."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from nextfight.core.config import Settings


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create the process-wide asynchronous PostgreSQL engine."""
    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout_seconds,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an asynchronous session factory bound to an engine."""
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
