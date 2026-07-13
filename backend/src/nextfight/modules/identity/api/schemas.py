"""Identity API contracts."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

BEARER_TOKEN_TYPE = "bearer"  # noqa: S105 - OAuth token scheme, not a credential.


class RegisterRequest(BaseModel):
    """New account input."""

    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=2, max_length=120)


class LoginRequest(BaseModel):
    """Password login input."""

    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Refresh or logout session input."""

    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=64, max_length=256)


class UserResponse(BaseModel):
    """Authenticated public user fields."""

    id: UUID
    email: EmailStr
    display_name: str
    role: str


class TokenResponse(BaseModel):
    """Access and rotating refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = BEARER_TOKEN_TYPE
    expires_in: int
    user: UserResponse
