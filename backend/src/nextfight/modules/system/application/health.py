"""Infrastructure readiness use case."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

from sqlalchemy import text

from nextfight.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from sqlalchemy.ext.asyncio import AsyncEngine

logger = get_logger(__name__)
DependencyStatus = Literal["healthy", "unhealthy"]


class RedisHealthClient(Protocol):
    """Minimal Redis contract required by operational health checks."""

    def ping(self) -> Awaitable[bool]:
        """Return whether Redis responds to a ping."""
        ...


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    """Result of all mandatory dependency checks."""

    dependencies: dict[str, DependencyStatus]

    @property
    def is_healthy(self) -> bool:
        """Return whether every mandatory dependency is healthy."""
        return all(status == "healthy" for status in self.dependencies.values())


class HealthService:
    """Check availability of mandatory infrastructure dependencies."""

    def __init__(
        self,
        *,
        database_engine: AsyncEngine,
        redis: RedisHealthClient,
        timeout_seconds: float,
    ) -> None:
        """Store dependency clients and the maximum check duration."""
        self._database_engine = database_engine
        self._redis = redis
        self._timeout_seconds = timeout_seconds

    async def check_readiness(self) -> ReadinessResult:
        """Check PostgreSQL and Redis concurrently with a bounded timeout."""
        database_status, redis_status = await asyncio.gather(
            self._check_database(),
            self._check_redis(),
        )
        return ReadinessResult(
            dependencies={
                "postgresql": database_status,
                "redis": redis_status,
            },
        )

    async def _check_database(self) -> DependencyStatus:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                async with self._database_engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
        except Exception as exception:  # noqa: BLE001
            logger.warning(
                "dependency_unavailable",
                dependency="postgresql",
                exception_type=type(exception).__name__,
            )
            return "unhealthy"
        return "healthy"

    async def _check_redis(self) -> DependencyStatus:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                await self._redis.ping()
        except Exception as exception:  # noqa: BLE001
            logger.warning(
                "dependency_unavailable",
                dependency="redis",
                exception_type=type(exception).__name__,
            )
            return "unhealthy"
        return "healthy"
