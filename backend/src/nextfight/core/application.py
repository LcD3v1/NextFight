"""FastAPI application factory and lifecycle composition."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from nextfight.api.router import build_router
from nextfight.core.config import Environment, Settings, get_settings
from nextfight.core.errors.handlers import register_exception_handlers
from nextfight.core.logging import configure_logging, get_logger
from nextfight.core.middleware.request_id import RequestIdMiddleware
from nextfight.infrastructure.cache.client import create_redis_client
from nextfight.infrastructure.database.session import create_database_engine

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = get_logger(__name__)


def create_application(settings: Settings | None = None) -> FastAPI:
    """Create a fully configured FastAPI application."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
        application.state.settings = resolved_settings
        application.state.database_engine = create_database_engine(resolved_settings)
        application.state.redis = create_redis_client(resolved_settings)
        logger.info("application_started", environment=resolved_settings.environment)
        try:
            yield
        finally:
            await application.state.redis.aclose()
            await application.state.database_engine.dispose()
            logger.info("application_stopped")

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        docs_url=None
        if resolved_settings.environment is Environment.PRODUCTION
        else "/docs",
        redoc_url=None,
        openapi_url=None
        if resolved_settings.environment is Environment.PRODUCTION
        else "/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(build_router())
    return app
