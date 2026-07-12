"""Operational health endpoints."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from nextfight.core.errors.handlers import problem_response
from nextfight.modules.system.api.dependencies import get_health_service
from nextfight.modules.system.api.schemas import HealthResponse
from nextfight.modules.system.application.health import HealthService

router = APIRouter(prefix="/health", tags=["System"])


@router.get("/live")
async def liveness(request: Request) -> HealthResponse:
    """Confirm that the API process can serve requests."""
    return HealthResponse(
        status="healthy",
        environment=request.app.state.settings.environment,
        version=request.app.state.settings.app_version,
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    responses={
        HTTPStatus.SERVICE_UNAVAILABLE: {"description": "Dependency unavailable"},
    },
)
async def readiness(
    request: Request,
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse | JSONResponse:
    """Confirm that required infrastructure dependencies are available."""
    result = await health_service.check_readiness()
    if not result.is_healthy:
        return problem_response(
            request=request,
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            title="Service Unavailable",
            detail="One or more required dependencies are unavailable.",
            error_type="https://nextfight.app/problems/dependency-unavailable",
            extensions={"dependencies": result.dependencies},
        )
    return HealthResponse(
        status="healthy",
        environment=request.app.state.settings.environment,
        version=request.app.state.settings.app_version,
        dependencies=result.dependencies,
    )
