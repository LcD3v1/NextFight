"""FastAPI database transaction dependencies."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_database_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide one atomic database session per request."""
    session = AsyncSession(
        bind=request.app.state.database_engine, expire_on_commit=False
    )
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
