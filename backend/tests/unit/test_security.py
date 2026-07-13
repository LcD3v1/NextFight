"""Identity security primitive tests."""

from uuid import uuid4

import pytest

from nextfight.core.config import Settings
from nextfight.modules.identity.domain.security import (
    InvalidAccessTokenError,
    PasswordHasher,
    TokenService,
)


def test_password_hash_uses_argon2id_and_verifies() -> None:
    """Passwords use Argon2id and reject mismatched plaintext."""
    hasher = PasswordHasher()
    password_hash = hasher.hash("correct horse battery staple")
    assert password_hash.startswith("$argon2id$")
    assert hasher.verify("correct horse battery staple", password_hash)
    assert not hasher.verify("wrong password", password_hash)


def test_access_token_round_trip_and_tamper_rejection() -> None:
    """JWT claims round-trip while signature tampering is rejected."""
    subject = uuid4()
    service = TokenService(Settings())
    token = service.issue_access_token(subject, "user")
    claims = service.decode_access_token(token)
    assert claims.subject == subject
    assert claims.role == "user"
    with pytest.raises(InvalidAccessTokenError):
        service.decode_access_token(f"{token}tampered")


def test_refresh_tokens_are_random_and_stored_as_hashes() -> None:
    """Refresh tokens have entropy and a non-reversible stored form."""
    first = TokenService.issue_refresh_token()
    second = TokenService.issue_refresh_token()
    assert first != second
    assert TokenService.hash_refresh_token(first) != first
