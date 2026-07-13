"""Reliable database-backed push delivery worker."""

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from nextfight.core.config import Settings
from nextfight.core.logging import get_logger
from nextfight.infrastructure.database.entities import AlertDelivery, Device
from nextfight.infrastructure.notifications.providers import (
    ApnsPushProvider,
    FcmPushProvider,
    PushConfigurationError,
    PushMessage,
    PushProvider,
    PushResult,
)

logger = get_logger(__name__)
MAX_DELIVERY_ATTEMPTS = 5


class PushProviderRegistry:
    """Lazily construct and retain platform provider adapters."""

    def __init__(self, settings: Settings) -> None:
        """Retain environment configuration without loading credentials eagerly."""
        self._settings = settings
        self._providers: dict[str, PushProvider] = {}

    def get(self, platform: str) -> PushProvider:
        """Return the provider for a supported device platform."""
        if platform not in self._providers:
            if platform == "android":
                self._providers[platform] = FcmPushProvider(self._settings)
            elif platform == "ios":
                self._providers[platform] = ApnsPushProvider(self._settings)
            else:
                message = f"Unsupported platform: {platform}"
                error = PushConfigurationError(message)
                raise error
        return self._providers[platform]

    async def close(self) -> None:
        """Close adapters that own network clients."""
        for provider in self._providers.values():
            if isinstance(provider, ApnsPushProvider):
                await provider.close()


class PushDeliveryWorker:
    """Claim pending deliveries and submit them with bounded backoff."""

    def __init__(self, engine: AsyncEngine, settings: Settings) -> None:
        """Bind worker to durable queue storage and provider configuration."""
        self._sessions = async_sessionmaker(engine, expire_on_commit=False)
        self._providers = PushProviderRegistry(settings)

    async def dispatch_batch(self, batch_size: int = 100) -> int:
        """Attempt one skip-locked batch and return processed item count."""
        now = datetime.now(UTC)
        processed = 0
        async with self._sessions.begin() as session:
            rows = (
                await session.execute(
                    select(AlertDelivery, Device)
                    .join(Device, Device.id == AlertDelivery.device_id)
                    .where(
                        AlertDelivery.status == "pending",
                        AlertDelivery.next_attempt_at <= now,
                        Device.notifications_enabled.is_(True),
                    )
                    .order_by(
                        AlertDelivery.next_attempt_at,
                        AlertDelivery.created_at,
                    )
                    .with_for_update(of=AlertDelivery, skip_locked=True)
                    .limit(batch_size)
                )
            ).all()
            for delivery, device in rows:
                delivery.attempts += 1
                delivery.attempted_at = now
                try:
                    provider = self._providers.get(device.platform)
                    result = await provider.send(
                        PushMessage(
                            token=device.push_token,
                            title=delivery.title,
                            body=delivery.body,
                            data={
                                key: str(value) for key, value in delivery.data.items()
                            },
                        )
                    )
                except Exception as error:  # noqa: BLE001 - provider failures are retried.
                    result = PushResult(
                        accepted=False,
                        error_code=type(error).__name__,
                    )
                self.apply_result(delivery, device, result, now)
                processed += 1
        return processed

    async def run(self, stop: asyncio.Event) -> None:
        """Continuously process due deliveries until graceful shutdown."""
        while not stop.is_set():
            try:
                processed = await self.dispatch_batch()
            except Exception as error:  # noqa: BLE001 - worker survives database outages.
                processed = 0
                logger.warning(
                    "push_dispatch_unavailable",
                    error_type=type(error).__name__,
                )
            if processed == 0:
                try:
                    await asyncio.wait_for(stop.wait(), timeout=1)
                except TimeoutError:
                    continue

    async def close(self) -> None:
        """Release provider network resources."""
        await self._providers.close()

    @staticmethod
    def apply_result(
        delivery: AlertDelivery,
        device: Device,
        result: PushResult,
        now: datetime,
    ) -> None:
        """Apply normalized provider results to durable delivery state."""
        delivery.provider_message_id = result.message_id
        delivery.error_code = result.error_code
        if result.accepted:
            delivery.status = "accepted"
            delivery.delivered_at = now
            return
        if result.invalid_token:
            device.notifications_enabled = False
        if result.invalid_token or delivery.attempts >= MAX_DELIVERY_ATTEMPTS:
            delivery.status = "failed"
            return
        delivery.next_attempt_at = now + timedelta(
            seconds=min(300, 2**delivery.attempts)
        )
