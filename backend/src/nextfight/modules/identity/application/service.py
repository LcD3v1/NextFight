"""Registration and rotating-session use cases."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    OneTimeToken,
    RefreshSession,
    User,
)
from nextfight.modules.identity.domain.security import PasswordHasher, TokenService


class IdentityError(ValueError):
    """Stable identity failure safe for API translation."""

    def __init__(self, code: str, message: str) -> None:
        """Create a stable error with a machine-readable code."""
        super().__init__(message)
        self.code = code


class IdentityService:
    """Coordinate user credentials and refresh-token rotation."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Bind identity use cases to one atomic request transaction."""
        self._session = session
        self._settings = settings
        self._passwords = PasswordHasher()
        self._tokens = TokenService(settings)

    async def register(
        self,
        email: str,
        password: str,
        display_name: str,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[User, str, str]:
        """Create a unique user and an initial authenticated session."""
        normalized_email = email.strip().casefold()
        if await self._find_user_by_email(normalized_email) is not None:
            error = _identity_error("email_unavailable", "This email cannot be used.")
            raise error
        user = User(
            email=normalized_email,
            password_hash=self._passwords.hash(password),
            display_name=display_name.strip(),
            locale="en",
            timezone="UTC",
            status="active",
            role="user",
        )
        self._session.add(user)
        await self._session.flush()
        access, refresh = await self._create_session(
            user, uuid4(), user_agent, ip_address
        )
        return user, access, refresh

    async def login(
        self,
        email: str,
        password: str,
        *,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[User, str, str]:
        """Authenticate credentials without revealing which field failed."""
        user = await self._find_user_by_email(email.strip().casefold())
        if (
            user is None
            or not self._passwords.verify(password, user.password_hash)
            or user.status != "active"
        ):
            error = _identity_error("invalid_credentials", "Invalid email or password.")
            raise error
        access, refresh = await self._create_session(
            user, uuid4(), user_agent, ip_address
        )
        return user, access, refresh

    async def refresh(
        self, refresh_token: str, *, user_agent: str | None, ip_address: str | None
    ) -> tuple[User, str, str]:
        """Rotate a valid refresh token and revoke its predecessor."""
        token_hash = self._tokens.hash_refresh_token(refresh_token)
        current = await self._session.scalar(
            select(RefreshSession)
            .where(RefreshSession.token_hash == token_hash)
            .with_for_update()
        )
        now = datetime.now(UTC)
        if current is None:
            error = _identity_error("invalid_refresh_token", "The session is invalid.")
            raise error
        if current.revoked_at is not None:
            await self._revoke_family(current.family_id, now)
            # Persist compromise containment even though the HTTP request fails.
            # Rolling this transaction back would leave the replacement usable.
            await self._session.commit()
            error = _identity_error(
                "refresh_token_reused", "The session has been revoked."
            )
            raise error
        if current.expires_at <= now:
            current.revoked_at = now
            error = _identity_error("refresh_token_expired", "The session has expired.")
            raise error
        user = await self._session.get(User, current.user_id)
        if user is None or user.status != "active":
            error = _identity_error("invalid_refresh_token", "The session is invalid.")
            raise error
        access, replacement_token = await self._create_session(
            user, current.family_id, user_agent, ip_address
        )
        replacement = await self._session.scalar(
            select(RefreshSession).where(
                RefreshSession.token_hash
                == self._tokens.hash_refresh_token(replacement_token)
            )
        )
        current.revoked_at = now
        current.replaced_by_id = replacement.id if replacement else None
        return user, access, replacement_token

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token when it exists, preserving idempotency."""
        token_hash = self._tokens.hash_refresh_token(refresh_token)
        session = await self._session.scalar(
            select(RefreshSession)
            .where(RefreshSession.token_hash == token_hash)
            .with_for_update()
        )
        if session is not None and session.revoked_at is None:
            session.revoked_at = datetime.now(UTC)

    async def request_password_reset(self, email: str) -> tuple[User, str] | None:
        """Create a short-lived opaque token without revealing unknown accounts."""
        user = await self._find_user_by_email(email.strip().casefold())
        if user is None or user.status != "active":
            return None
        now = datetime.now(UTC)
        await self._session.execute(
            update(OneTimeToken)
            .where(
                OneTimeToken.user_id == user.id,
                OneTimeToken.purpose == "password_reset",
                OneTimeToken.consumed_at.is_(None),
            )
            .values(consumed_at=now)
        )
        token = self._tokens.issue_refresh_token()
        self._session.add(
            OneTimeToken(
                user_id=user.id,
                purpose="password_reset",
                token_hash=self._tokens.hash_refresh_token(token),
                expires_at=now
                + timedelta(minutes=self._settings.password_reset_minutes),
            )
        )
        await self._session.flush()
        return user, token

    async def reset_password(self, token: str, password: str) -> None:
        """Consume a recovery token, replace the hash, and revoke all sessions."""
        token_record = await self._session.scalar(
            select(OneTimeToken)
            .where(
                OneTimeToken.token_hash == self._tokens.hash_refresh_token(token),
                OneTimeToken.purpose == "password_reset",
            )
            .with_for_update()
        )
        now = datetime.now(UTC)
        if (
            token_record is None
            or token_record.consumed_at is not None
            or token_record.expires_at <= now
        ):
            error = _identity_error(
                "invalid_reset_token", "The reset token is invalid or expired."
            )
            raise error
        user = await self._session.get(User, token_record.user_id)
        if user is None or user.status != "active":
            error = _identity_error(
                "invalid_reset_token", "The reset token is invalid or expired."
            )
            raise error
        user.password_hash = self._passwords.hash(password)
        token_record.consumed_at = now
        await self._session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.user_id == user.id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

    async def update_profile(
        self,
        user: User,
        *,
        display_name: str | None,
        locale: str | None,
        timezone: str | None,
    ) -> User:
        """Update validated profile fields without replacing omitted values."""
        if timezone is not None:
            try:
                ZoneInfo(timezone)
            except ZoneInfoNotFoundError as exception:
                error = _identity_error("invalid_timezone", "Invalid timezone.")
                raise error from exception
            user.timezone = timezone
        if display_name is not None:
            user.display_name = display_name.strip()
        if locale is not None:
            user.locale = locale
        await self._session.flush()
        return user

    async def _find_user_by_email(self, email: str) -> User | None:
        return await self._session.scalar(select(User).where(User.email == email))

    async def _create_session(
        self,
        user: User,
        family_id: UUID,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[str, str]:
        refresh_token = self._tokens.issue_refresh_token()
        self._session.add(
            RefreshSession(
                user_id=user.id,
                family_id=family_id,
                token_hash=self._tokens.hash_refresh_token(refresh_token),
                expires_at=datetime.now(UTC)
                + timedelta(days=self._settings.refresh_token_days),
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        await self._session.flush()
        return self._tokens.issue_access_token(user.id, user.role), refresh_token

    async def _revoke_family(self, family_id: UUID, revoked_at: datetime) -> None:
        await self._session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == family_id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )


def _identity_error(code: str, message: str) -> IdentityError:
    """Build an identity error without coupling callers to transport concerns."""
    return IdentityError(code, message)
