"""Problem Details handler tests."""

from http import HTTPStatus

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from nextfight.core.errors.handlers import (
    handle_unexpected_exception,
    handle_validation_exception,
)


def build_request() -> Request:
    """Build a minimal concrete ASGI request for handler tests."""
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/test",
            "raw_path": b"/test",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "state": {"request_id": "test-request-id"},
        },
    )


async def test_validation_handler_exposes_safe_field_errors() -> None:
    """Validation errors include location, message, and stable code."""
    exception = RequestValidationError(
        [
            {
                "type": "missing",
                "loc": ("query", "name"),
                "msg": "Field required",
                "input": None,
            },
        ],
    )

    response = await handle_validation_exception(build_request(), exception)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert b'"location":"query.name"' in response.body
    assert b'"request_id":"test-request-id"' in response.body


async def test_unexpected_handler_hides_internal_details() -> None:
    """Unexpected exceptions never expose their original message."""
    response = await handle_unexpected_exception(
        build_request(),
        RuntimeError("sensitive internal detail"),
    )

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert b"sensitive internal detail" not in response.body
    assert b"An unexpected error occurred" in response.body
