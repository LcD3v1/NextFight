"""Global RFC 9457 Problem Details exception handling."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from nextfight.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

logger = get_logger(__name__)
PROBLEM_MEDIA_TYPE = "application/problem+json"


def problem_response(  # noqa: PLR0913 - RFC 9457 defines these independent fields.
    *,
    request: Request,
    status: int,
    title: str,
    detail: str,
    error_type: str = "about:blank",
    extensions: dict[str, Any] | None = None,
) -> JSONResponse:
    """Create a Problem Details response with trace correlation."""
    body: dict[str, Any] = {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": str(request.url.path),
        "request_id": request.state.request_id,
    }
    if extensions:
        body.update(extensions)
    return JSONResponse(body, status_code=status, media_type=PROBLEM_MEDIA_TYPE)


async def handle_http_exception(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Convert framework HTTP errors to Problem Details."""
    if not isinstance(exception, HTTPException):
        return await handle_unexpected_exception(request, exception)
    status = exception.status_code
    title = (
        HTTPStatus(status).phrase
        if status in HTTPStatus._value2member_map_
        else "Error"
    )
    return problem_response(
        request=request,
        status=status,
        title=title,
        detail=str(exception.detail),
    )


async def handle_validation_exception(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Convert request validation errors to safe field-level details."""
    if not isinstance(exception, RequestValidationError):
        return await handle_unexpected_exception(request, exception)
    errors = [
        {
            "location": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        }
        for error in exception.errors()
    ]
    return problem_response(
        request=request,
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        title="Validation Error",
        detail="The request contains invalid data.",
        error_type="https://nextfight.app/problems/validation-error",
        extensions={"errors": errors},
    )


async def handle_unexpected_exception(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """Log unexpected failures and return a non-sensitive response."""
    logger.exception(
        "unhandled_exception",
        request_id=request.state.request_id,
        path=request.url.path,
        exception_type=type(exception).__name__,
    )
    return problem_response(
        request=request,
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)
