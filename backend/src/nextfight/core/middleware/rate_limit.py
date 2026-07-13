"""Redis-backed fixed-window request rate limiting."""

from __future__ import annotations

from http import HTTPStatus
from time import time
from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from nextfight.core.config import Environment
from nextfight.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import Request, Response
    from starlette.types import ASGIApp

logger = get_logger(__name__)
AUTH_PATHS = {
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply distributed per-client limits across application replicas."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware without opening external resources."""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Count the current window and reject requests beyond policy."""
        if request.method == "OPTIONS" or request.url.path in {"/health", "/live"}:
            return await call_next(request)
        settings = request.app.state.settings
        is_auth = request.url.path in AUTH_PATHS
        limit = (
            settings.auth_rate_limit_per_minute
            if is_auth
            else settings.api_rate_limit_per_minute
        )
        client = request.client.host if request.client else "unknown"
        window = int(time() // 60)
        key = (
            f"{settings.rate_limit_namespace}:rate:{request.url.path}:{client}:{window}"
        )
        try:
            pipeline = request.app.state.redis.pipeline(transaction=True)
            pipeline.incr(key)
            pipeline.expire(key, 61)
            count, _ = await pipeline.execute()
        except Exception as error:  # noqa: BLE001 - policy handles cache outages.
            logger.warning("rate_limit_unavailable", error_type=type(error).__name__)
            if is_auth and settings.environment is Environment.PRODUCTION:
                return _error(request, HTTPStatus.SERVICE_UNAVAILABLE, limit)
            return await call_next(request)
        remaining = max(0, limit - int(count))
        if int(count) > limit:
            return _error(request, HTTPStatus.TOO_MANY_REQUESTS, limit)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def _error(request: Request, status: HTTPStatus, limit: int) -> JSONResponse:
    """Return a safe Problem Details-compatible rate-limit response."""
    response = JSONResponse(
        {
            "type": "https://nextfight.app/problems/rate-limit",
            "title": status.phrase,
            "status": status.value,
            "detail": "Request rate limit exceeded. Try again shortly.",
            "instance": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
        },
        status_code=status.value,
        media_type="application/problem+json",
    )
    response.headers["Retry-After"] = "60"
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = "0"
    return response
