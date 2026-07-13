"""SQLAlchemy repository integration tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import User
from nextfight.infrastructure.database.repository import SqlAlchemyRepository
from nextfight.infrastructure.database.session import create_database_engine


@pytest.mark.integration
async def test_repository_persists_and_loads_entity(settings: Settings) -> None:
    """Repository flushes and reloads a typed entity in a real transaction."""
    engine = create_database_engine(settings)
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    try:
        repository = SqlAlchemyRepository(session, User)
        user = User(
            email="repository-test@nextfight.invalid",
            password_hash="not-a-credential",  # noqa: S106 - persisted only in rolled-back test transaction.
            display_name="Repository Test",
            locale="en",
            timezone="UTC",
            status="active",
        )
        await repository.add(user)
        user_id = user.id
        session.expunge(user)
        loaded = await repository.get(user_id)
        assert loaded is not None
        assert loaded.email == "repository-test@nextfight.invalid"
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
        await engine.dispose()
