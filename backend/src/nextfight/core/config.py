"""Validated application configuration."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment environments."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Supported structured logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_name: str = "NextFight API"
    app_version: str = "0.1.0"
    environment: Environment = Field(
        default=Environment.LOCAL,
        validation_alias="NEXTFIGHT_ENV",
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        validation_alias="NEXTFIGHT_LOG_LEVEL",
    )
    database_url: str = Field(
        default="postgresql+asyncpg://nextfight:local-nextfight-password@localhost:5432/nextfight",
        validation_alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=200)
    database_pool_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    redis_url: SecretStr = Field(
        default=SecretStr("redis://localhost:6379/0"),
        validation_alias="REDIS_URL",
    )
    health_check_timeout_seconds: float = Field(default=2.0, gt=0, le=10)
    jwt_secret: SecretStr = Field(
        default=SecretStr("local-development-secret-change-me"),
        validation_alias="JWT_SECRET",
    )
    jwt_issuer: str = "https://api.nextfight.app"
    jwt_audience: str = "nextfight-clients"
    access_token_minutes: int = Field(default=15, ge=5, le=30)
    refresh_token_days: int = Field(default=30, ge=1, le=90)
    manual_override_minutes: int = Field(default=10, ge=1, le=60)

    @field_validator("database_url")
    @classmethod
    def validate_database_driver(cls, value: str) -> str:
        """Require the asynchronous PostgreSQL driver."""
        if not value.startswith("postgresql+asyncpg://"):
            msg = "DATABASE_URL must use the postgresql+asyncpg driver"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Settings:
        """Reject development credentials in production."""
        if (
            self.environment is Environment.PRODUCTION
            and self.jwt_secret.get_secret_value()
            == "local-development-secret-change-me"
        ):
            msg = "JWT_SECRET must be replaced in production"
            raise ValueError(msg)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
