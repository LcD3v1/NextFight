"""Operational endpoint integration tests."""

from http import HTTPStatus

import httpx
import pytest


@pytest.mark.integration
async def test_liveness_endpoint(client: httpx.AsyncClient) -> None:
    """Liveness exposes process status and deployment metadata."""
    response = await client.get("/health/live")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "status": "healthy",
        "environment": "local",
        "version": "0.1.0",
        "dependencies": None,
    }


@pytest.mark.integration
async def test_readiness_checks_real_dependencies(client: httpx.AsyncClient) -> None:
    """Readiness verifies real PostgreSQL and Redis connections."""
    response = await client.get("/health/ready")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["dependencies"] == {
        "postgresql": "healthy",
        "redis": "healthy",
    }


async def test_not_found_uses_problem_details(client: httpx.AsyncClient) -> None:
    """Framework HTTP errors use the documented Problem Details contract."""
    response = await client.get("/does-not-exist")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["status"] == HTTPStatus.NOT_FOUND
    assert body["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.integration
async def test_readiness_reports_unavailable_dependencies(
    unavailable_client: httpx.AsyncClient,
) -> None:
    """Readiness fails safely when required sockets cannot be reached."""
    response = await unavailable_client.get("/health/ready")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["dependencies"] == {
        "postgresql": "unhealthy",
        "redis": "unhealthy",
    }
