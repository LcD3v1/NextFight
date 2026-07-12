"""Shared integration test fixtures."""

from collections.abc import AsyncIterator

import httpx
import pytest
from pydantic import SecretStr

from nextfight.core.application import create_application
from nextfight.core.config import Environment, LogLevel, Settings


@pytest.fixture
def settings() -> Settings:
    """Return test settings backed by local real services."""
    return Settings(
        environment=Environment.LOCAL,
        log_level=LogLevel.CRITICAL,
        database_url="postgresql+asyncpg://nextfight:local-nextfight-password@localhost:5432/nextfight",
        redis_url=SecretStr("redis://localhost:6379/15"),
    )


@pytest.fixture
async def client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
    """Yield an HTTP client while running the full application lifecycle."""
    app = create_application(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client


@pytest.fixture
async def unavailable_client() -> AsyncIterator[httpx.AsyncClient]:
    """Yield a client configured with deliberately unavailable real sockets."""
    settings = Settings(
        environment=Environment.LOCAL,
        log_level=LogLevel.CRITICAL,
        database_url="postgresql+asyncpg://nextfight:unused@127.0.0.1:1/nextfight",
        redis_url=SecretStr("redis://127.0.0.1:1/15"),
        health_check_timeout_seconds=0.1,
    )
    app = create_application(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client
