"""FastAPI application factory and lifecycle composition."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nextfight.api.router import build_router
from nextfight.core.config import Environment, Settings, get_settings
from nextfight.core.errors.handlers import register_exception_handlers
from nextfight.core.logging import configure_logging, get_logger
from nextfight.core.middleware.request_id import RequestIdMiddleware
from nextfight.infrastructure.cache.client import create_redis_client
from nextfight.infrastructure.database.session import create_database_engine
from nextfight.infrastructure.messaging.outbox import OutboxDispatcher
from nextfight.infrastructure.notifications.scheduler import LeadTimeAlertScheduler
from nextfight.infrastructure.notifications.worker import PushDeliveryWorker

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
        application.state.outbox_stop = asyncio.Event()
        dispatcher = OutboxDispatcher(
            application.state.database_engine, application.state.redis
        )
        outbox_task = asyncio.create_task(
            dispatcher.run(application.state.outbox_stop), name="outbox-dispatcher"
        )
        application.state.push_stop = asyncio.Event()
        push_worker = PushDeliveryWorker(
            application.state.database_engine, resolved_settings
        )
        push_task = asyncio.create_task(
            push_worker.run(application.state.push_stop), name="push-delivery-worker"
        )
        lead_time_scheduler = LeadTimeAlertScheduler(application.state.database_engine)
        lead_time_task = asyncio.create_task(
            lead_time_scheduler.run(application.state.push_stop),
            name="lead-time-alert-scheduler",
        )
        logger.info("application_started", environment=resolved_settings.environment)
        try:
            yield
        finally:
            application.state.outbox_stop.set()
            application.state.push_stop.set()
            await asyncio.gather(outbox_task, push_task, lead_time_task)
            await push_worker.close()
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(build_router())
    return app
