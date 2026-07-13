"""Production push notification provider adapters."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Protocol
from uuid import uuid4

import firebase_admin
import httpx
import jwt
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from nextfight.core.config import Settings


@dataclass(frozen=True, slots=True)
class PushMessage:
    """Provider-neutral push notification."""

    token: str
    title: str
    body: str
    data: dict[str, str]


@dataclass(frozen=True, slots=True)
class PushResult:
    """Normalized provider acceptance result."""

    accepted: bool
    message_id: str | None = None
    error_code: str | None = None
    invalid_token: bool = False


class PushProvider(Protocol):
    """Port implemented by a platform push provider."""

    async def send(self, message: PushMessage) -> PushResult:
        """Submit one notification to the provider."""
        ...


class PushConfigurationError(RuntimeError):
    """Raised when a platform provider has no environment credentials."""


FCM_NOT_CONFIGURED = "FCM credentials are not configured."
APNS_NOT_CONFIGURED = "APNs credentials are not configured."


class FcmPushProvider:
    """Firebase Cloud Messaging adapter using the official Admin SDK."""

    def __init__(self, settings: Settings) -> None:
        """Initialize an isolated Firebase application from a service account."""
        if settings.fcm_credentials_path is None:
            error = PushConfigurationError(FCM_NOT_CONFIGURED)
            raise error
        credential = credentials.Certificate(str(settings.fcm_credentials_path))
        self._app = firebase_admin.initialize_app(
            credential, name=f"nextfight-{uuid4()}"
        )

    async def send(self, message: PushMessage) -> PushResult:
        """Submit a typed notification without blocking the event loop."""
        notification = messaging.Message(
            token=message.token,
            notification=messaging.Notification(
                title=message.title,
                body=message.body,
            ),
            data=message.data,
        )
        try:
            message_id = await asyncio.to_thread(
                messaging.send, notification, app=self._app
            )
            return PushResult(accepted=True, message_id=message_id)
        except messaging.UnregisteredError:
            return PushResult(
                accepted=False,
                error_code="unregistered",
                invalid_token=True,
            )
        except FirebaseError as error:
            raw_code: object = getattr(error, "code", None)
            error_code = raw_code if isinstance(raw_code, str) else "firebase_error"
            return PushResult(accepted=False, error_code=error_code)


class ApnsPushProvider:
    """Apple Push Notification service HTTP/2 token adapter."""

    def __init__(self, settings: Settings) -> None:
        """Validate APNs token credentials and configure an HTTP/2 client."""
        if not all(
            (
                settings.apns_team_id,
                settings.apns_key_id,
                settings.apns_bundle_id,
                settings.apns_private_key,
            )
        ):
            error = PushConfigurationError(APNS_NOT_CONFIGURED)
            raise error
        self._team_id = settings.apns_team_id or ""
        self._key_id = settings.apns_key_id or ""
        self._bundle_id = settings.apns_bundle_id or ""
        self._private_key = (
            settings.apns_private_key.get_secret_value()
            if settings.apns_private_key
            else ""
        )
        host = (
            "https://api.sandbox.push.apple.com"
            if settings.apns_use_sandbox
            else "https://api.push.apple.com"
        )
        self._client = httpx.AsyncClient(base_url=host, http2=True, timeout=10)
        self._authorization: tuple[str, datetime] | None = None

    async def send(self, message: PushMessage) -> PushResult:
        """Submit an APNs alert and classify permanent token failures."""
        response = await self._client.post(
            f"/3/device/{message.token}",
            headers={
                "authorization": f"bearer {self._provider_token()}",
                "apns-topic": self._bundle_id,
                "apns-push-type": "alert",
                "apns-priority": "10",
            },
            json={
                "aps": {
                    "alert": {"title": message.title, "body": message.body},
                    "sound": "default",
                },
                **message.data,
            },
        )
        if response.status_code == HTTPStatus.OK:
            return PushResult(
                accepted=True,
                message_id=response.headers.get("apns-id"),
            )
        reason = apns_reason(response)
        return PushResult(
            accepted=False,
            error_code=reason,
            invalid_token=reason in {"BadDeviceToken", "Unregistered"},
        )

    async def close(self) -> None:
        """Close pooled APNs HTTP/2 connections."""
        await self._client.aclose()

    def _provider_token(self) -> str:
        now = datetime.now(UTC)
        if self._authorization and now - self._authorization[1] < timedelta(minutes=50):
            return self._authorization[0]
        token = jwt.encode(
            {"iss": self._team_id, "iat": int(now.timestamp())},
            self._private_key,
            algorithm="ES256",
            headers={"kid": self._key_id},
        )
        self._authorization = (token, now)
        return token


def apns_reason(response: httpx.Response) -> str:
    """Extract a stable APNs rejection reason from a provider response."""
    try:
        reason = response.json().get("reason")
    except ValueError:
        return f"http_{response.status_code}"
    return str(reason or f"http_{response.status_code}")
