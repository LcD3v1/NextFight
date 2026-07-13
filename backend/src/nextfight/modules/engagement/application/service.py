"""Favorites, fight alerts, and push device use cases."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.entities import (
    Alert,
    Athlete,
    Device,
    Event,
    Favorite,
    Fight,
    Organization,
)
from nextfight.modules.engagement.api.schemas import (
    AlertCreate,
    AlertUpdate,
    DeviceCreate,
    FavoriteCreate,
)


class EngagementNotFoundError(LookupError):
    """Raised when an owned engagement resource does not exist."""


class InvalidEngagementTargetError(ValueError):
    """Raised when a referenced domain target does not exist."""


class EngagementService:
    """Manage user-owned engagement resources transactionally."""

    def __init__(self, session: AsyncSession, user_id: UUID) -> None:
        """Bind use cases to an authenticated user and request transaction."""
        self._session = session
        self._user_id = user_id

    async def list_favorites(self) -> list[Favorite]:
        """Return the user's favorites in reverse creation order."""
        return list(
            await self._session.scalars(
                select(Favorite)
                .where(Favorite.user_id == self._user_id)
                .order_by(Favorite.created_at.desc(), Favorite.id)
            )
        )

    async def create_favorite(self, payload: FavoriteCreate) -> Favorite:
        """Idempotently favorite an existing supported target."""
        await self._ensure_target(payload.target_type, payload.target_id)
        existing = await self._session.scalar(
            select(Favorite).where(
                Favorite.user_id == self._user_id,
                Favorite.target_type == payload.target_type,
                Favorite.target_id == payload.target_id,
            )
        )
        if existing is not None:
            return existing
        favorite = Favorite(user_id=self._user_id, **payload.model_dump())
        self._session.add(favorite)
        await self._session.flush()
        return favorite

    async def delete_favorite(self, favorite_id: UUID) -> None:
        """Delete only a favorite owned by the authenticated user."""
        result = await self._session.execute(
            delete(Favorite).where(
                Favorite.id == favorite_id, Favorite.user_id == self._user_id
            )
        )
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise EngagementNotFoundError

    async def list_alerts(self) -> list[Alert]:
        """Return the user's alert configuration and history."""
        return list(
            await self._session.scalars(
                select(Alert)
                .where(Alert.user_id == self._user_id)
                .order_by(Alert.created_at.desc(), Alert.id)
            )
        )

    async def create_alert(self, payload: AlertCreate) -> Alert:
        """Create or reactivate an idempotent alert for an existing fight."""
        if await self._session.get(Fight, payload.fight_id) is None:
            raise InvalidEngagementTargetError
        lead_minutes = (
            payload.lead_minutes if payload.trigger_type == "lead_time" else None
        )
        if payload.trigger_type == "lead_time" and lead_minutes is None:
            raise InvalidEngagementTargetError
        existing = await self._session.scalar(
            select(Alert).where(
                Alert.user_id == self._user_id,
                Alert.fight_id == payload.fight_id,
                Alert.trigger_type == payload.trigger_type,
                Alert.lead_minutes == lead_minutes,
            )
        )
        if existing is not None:
            existing.status = "active"
            existing.cancelled_at = None
            return existing
        alert = Alert(
            user_id=self._user_id,
            fight_id=payload.fight_id,
            trigger_type=payload.trigger_type,
            lead_minutes=lead_minutes,
            status="active",
        )
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def update_alert(self, alert_id: UUID, payload: AlertUpdate) -> Alert:
        """Update an owned active or paused alert."""
        alert = await self._owned_alert(alert_id)
        if payload.status is not None:
            alert.status = payload.status
        if payload.lead_minutes is not None:
            if alert.trigger_type != "lead_time":
                raise InvalidEngagementTargetError
            alert.lead_minutes = payload.lead_minutes
        await self._session.flush()
        await self._session.refresh(alert)
        return alert

    async def delete_alert(self, alert_id: UUID) -> None:
        """Soft-cancel an owned alert while preserving its history."""
        alert = await self._owned_alert(alert_id)
        alert.status = "cancelled"
        alert.cancelled_at = datetime.now(UTC)

    async def list_devices(self) -> list[Device]:
        """Return the user's registered notification devices."""
        return list(
            await self._session.scalars(
                select(Device)
                .where(Device.user_id == self._user_id)
                .order_by(Device.last_seen_at.desc(), Device.id)
            )
        )

    async def register_device(self, payload: DeviceCreate) -> Device:
        """Upsert a provider token, transferring it to the current account."""
        device = await self._session.scalar(
            select(Device).where(Device.push_token == payload.push_token)
        )
        if device is None:
            device = Device(user_id=self._user_id, **payload.model_dump())
            self._session.add(device)
        else:
            device.user_id = self._user_id
            device.platform = payload.platform
            device.app_version = payload.app_version
            device.notifications_enabled = payload.notifications_enabled
        device.last_seen_at = datetime.now(UTC)
        await self._session.flush()
        return device

    async def delete_device(self, device_id: UUID) -> None:
        """Delete only a device owned by the authenticated user."""
        result = await self._session.execute(
            delete(Device).where(
                Device.id == device_id, Device.user_id == self._user_id
            )
        )
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise EngagementNotFoundError

    async def _owned_alert(self, alert_id: UUID) -> Alert:
        alert = await self._session.scalar(
            select(Alert).where(Alert.id == alert_id, Alert.user_id == self._user_id)
        )
        if alert is None:
            raise EngagementNotFoundError
        return alert

    async def _ensure_target(self, target_type: str, target_id: UUID) -> None:
        entities = {"event": Event, "organization": Organization, "athlete": Athlete}
        if await self._session.get(entities[target_type], target_id) is None:
            raise InvalidEngagementTargetError
