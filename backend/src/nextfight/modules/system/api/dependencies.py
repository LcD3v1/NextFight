"""System module dependency providers."""

from typing import cast

from fastapi import Request

from nextfight.modules.system.application.health import HealthService, RedisHealthClient


def get_health_service(request: Request) -> HealthService:
    """Build the health service from application-owned resources."""
    return HealthService(
        database_engine=request.app.state.database_engine,
        redis=cast("RedisHealthClient", request.app.state.redis),
        timeout_seconds=request.app.state.settings.health_check_timeout_seconds,
    )
