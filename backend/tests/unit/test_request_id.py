"""Request correlation behavior tests."""

from http import HTTPStatus
from uuid import UUID

import httpx

UUID_VERSION_4 = 4


async def test_response_preserves_safe_request_id(client: httpx.AsyncClient) -> None:
    """A valid caller-provided request ID is returned unchanged."""
    response = await client.get("/health/live", headers={"X-Request-ID": "client-123"})

    assert response.status_code == HTTPStatus.OK
    assert response.headers["X-Request-ID"] == "client-123"


async def test_response_replaces_unsafe_request_id(client: httpx.AsyncClient) -> None:
    """An unsafe caller-provided request ID is replaced with a UUID."""
    response = await client.get("/health/live", headers={"X-Request-ID": "invalid id"})

    generated_request_id = response.headers["X-Request-ID"]
    assert UUID(generated_request_id).version == UUID_VERSION_4
