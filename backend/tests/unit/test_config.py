"""Configuration validation tests."""

import pytest
from pydantic import ValidationError

from nextfight.core.config import Environment, Settings


def test_settings_accept_supported_environment() -> None:
    """Supported deployment environments are parsed as enums."""
    settings = Settings(environment=Environment.STAGING)

    assert settings.environment is Environment.STAGING


def test_settings_reject_non_async_database_driver() -> None:
    """Synchronous database URLs are rejected during startup."""
    with pytest.raises(ValidationError, match=r"postgresql\+asyncpg"):
        Settings(database_url="postgresql://localhost/nextfight")
