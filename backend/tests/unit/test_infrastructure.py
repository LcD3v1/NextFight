"""Infrastructure construction tests."""

from sqlalchemy.ext.asyncio import AsyncEngine

from nextfight.core.config import get_settings
from nextfight.infrastructure.database.models import Base
from nextfight.infrastructure.database.session import (
    create_database_engine,
    create_session_factory,
)
from nextfight.main import app


async def test_database_factory_creates_typed_sessions() -> None:
    """The shared engine creates non-expiring asynchronous sessions."""
    engine = create_database_engine(get_settings())
    session_factory = create_session_factory(engine)

    assert isinstance(engine, AsyncEngine)
    assert session_factory.kw["expire_on_commit"] is False
    await engine.dispose()


def test_application_and_metadata_are_importable() -> None:
    """ASGI entry point and migration metadata load without side effects."""
    assert app.title == "NextFight API"
    assert Base.metadata.tables == {}
