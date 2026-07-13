"""Password and token security primitives."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from nextfight.core.config import Settings


class InvalidAccessTokenError(ValueError):
    """Raised when an access token is invalid or expired."""


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    """Validated claims required by authorization."""

    subject: UUID
    role: str
    token_id: UUID
    expires_at: datetime


class PasswordHasher:
    """Argon2id password hashing adapter."""

    def __init__(self) -> None:
        """Configure the recommended Argon2id hasher."""
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        """Create a salted Argon2id password hash."""
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a password using constant-time library primitives."""
        return self._hasher.verify(password, password_hash)


class TokenService:
    """Issue and validate short-lived access and opaque refresh tokens."""

    def __init__(self, settings: Settings) -> None:
        """Configure signing policy from validated settings."""
        self._secret = settings.jwt_secret.get_secret_value()
        self._issuer = settings.jwt_issuer
        self._audience = settings.jwt_audience
        self._access_lifetime = timedelta(minutes=settings.access_token_minutes)

    def issue_access_token(self, subject: UUID, role: str) -> str:
        """Issue a signed access token for an authenticated principal."""
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": str(subject),
            "role": role,
            "jti": str(uuid4()),
            "iat": now,
            "nbf": now,
            "exp": now + self._access_lifetime,
            "iss": self._issuer,
            "aud": self._audience,
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")  # pyright: ignore[reportUnknownMemberType]

    def decode_access_token(self, token: str) -> AccessTokenClaims:
        """Validate signature, registered claims, subject, and role."""
        try:
            payload = jwt.decode(  # pyright: ignore[reportUnknownMemberType]
                token,
                self._secret,
                algorithms=["HS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["sub", "role", "jti", "exp", "iat", "nbf"]},
            )
            return AccessTokenClaims(
                subject=UUID(payload["sub"]),
                role=str(payload["role"]),
                token_id=UUID(payload["jti"]),
                expires_at=datetime.fromtimestamp(payload["exp"], UTC),
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exception:
            raise InvalidAccessTokenError from exception

    @staticmethod
    def issue_refresh_token() -> str:
        """Create a cryptographically secure opaque refresh token."""
        return token_urlsafe(64)

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """Hash a refresh token before persistence."""
        return sha256(token.encode("utf-8")).hexdigest()
