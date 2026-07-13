"""Push provider normalization and delivery policy tests."""

from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import AlertDelivery, Device
from nextfight.infrastructure.notifications.providers import (
    PushConfigurationError,
    PushResult,
    apns_reason,
)
from nextfight.infrastructure.notifications.worker import (
    MAX_DELIVERY_ATTEMPTS,
    PushDeliveryWorker,
    PushProviderRegistry,
)


def _device() -> Device:
    return Device(
        user_id=uuid4(),
        platform="android",
        push_token="provider-token-value",  # noqa: S106 - non-secret test token.
        app_version="1.0.0",
        notifications_enabled=True,
        last_seen_at=datetime.now(UTC),
    )


def _delivery(*, attempts: int = 1) -> AlertDelivery:
    return AlertDelivery(
        alert_id=uuid4(),
        device_id=uuid4(),
        channel="push",
        idempotency_key=f"test:{uuid4()}",
        status="pending",
        title="Fight update",
        body="Your fight is next.",
        data={},
        attempts=attempts,
        next_attempt_at=datetime.now(UTC),
    )


def test_provider_registry_requires_environment_credentials() -> None:
    """Fail explicitly instead of silently dropping unconfigured pushes."""
    registry = PushProviderRegistry(Settings())
    with pytest.raises(PushConfigurationError):
        registry.get("android")
    with pytest.raises(PushConfigurationError):
        registry.get("ios")
    with pytest.raises(PushConfigurationError):
        registry.get("web")


def test_delivery_policy_accepts_provider_message() -> None:
    """Persist provider acceptance and its trace identifier."""
    delivery = _delivery()
    device = _device()
    now = datetime.now(UTC)
    PushDeliveryWorker.apply_result(
        delivery,
        device,
        PushResult(accepted=True, message_id="provider-message"),
        now,
    )
    assert delivery.status == "accepted"
    assert delivery.delivered_at == now
    assert delivery.provider_message_id == "provider-message"


def test_delivery_policy_disables_invalid_token() -> None:
    """Stop retrying a permanently invalid provider token."""
    delivery = _delivery()
    device = _device()
    PushDeliveryWorker.apply_result(
        delivery,
        device,
        PushResult(
            accepted=False,
            error_code="unregistered",
            invalid_token=True,
        ),
        datetime.now(UTC),
    )
    assert delivery.status == "failed"
    assert device.notifications_enabled is False


def test_delivery_policy_retries_then_dead_letters() -> None:
    """Back off transient failures and stop after the bounded attempt count."""
    retry = _delivery(attempts=2)
    before = retry.next_attempt_at
    PushDeliveryWorker.apply_result(
        retry,
        _device(),
        PushResult(accepted=False, error_code="timeout"),
        datetime.now(UTC),
    )
    assert retry.status == "pending"
    assert retry.next_attempt_at > before

    exhausted = _delivery(attempts=MAX_DELIVERY_ATTEMPTS)
    PushDeliveryWorker.apply_result(
        exhausted,
        _device(),
        PushResult(accepted=False, error_code="timeout"),
        datetime.now(UTC),
    )
    assert exhausted.status == "failed"


def test_apns_reason_handles_json_and_invalid_payloads() -> None:
    """Normalize APNs error bodies without trusting response shape."""
    assert apns_reason(httpx.Response(410, json={"reason": "Unregistered"})) == (
        "Unregistered"
    )
    assert apns_reason(httpx.Response(500, text="not-json")) == "http_500"
