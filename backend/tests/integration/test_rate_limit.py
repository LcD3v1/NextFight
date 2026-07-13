"""Distributed request rate-limit integration tests."""

from http import HTTPStatus
from uuid import uuid4

import httpx
import pytest

from nextfight.core.application import create_application
from nextfight.core.config import Settings


@pytest.mark.integration
async def test_authentication_rate_limit_uses_real_redis(
    settings: Settings,
) -> None:
    """Reject authentication abuse with traceable Problem Details metadata."""
    isolated = settings.model_copy(
        update={
            "rate_limit_namespace": f"nextfight-test-{uuid4().hex}",
            "auth_rate_limit_per_minute": 2,
        }
    )
    app = create_application(isolated)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://rate-limit-test"
        ) as client:
            for _ in range(2):
                accepted = await client.post(
                    "/api/v1/auth/forgot-password",
                    json={"email": f"unknown-{uuid4()}@example.com"},
                )
                assert accepted.status_code == HTTPStatus.ACCEPTED
            rejected = await client.post(
                "/api/v1/auth/forgot-password",
                json={"email": f"unknown-{uuid4()}@example.com"},
            )

    assert rejected.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert rejected.headers["content-type"].startswith("application/problem+json")
    assert rejected.headers["retry-after"] == "60"
    assert rejected.headers["x-request-id"]
    assert rejected.json()["request_id"] == rejected.headers["x-request-id"]
