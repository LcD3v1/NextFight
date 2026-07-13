"""Top-level API router composition."""

from fastapi import APIRouter

from nextfight.modules.engagement.api.router import router as engagement_router
from nextfight.modules.events.api.router import router as events_router
from nextfight.modules.identity.api.router import router as identity_router
from nextfight.modules.system.api.router import router as system_router


def build_router() -> APIRouter:
    """Build the application router from module-owned routers."""
    router = APIRouter()
    router.include_router(engagement_router, prefix="/api/v1")
    router.include_router(events_router, prefix="/api/v1")
    router.include_router(identity_router, prefix="/api/v1")
    router.include_router(system_router)
    return router
