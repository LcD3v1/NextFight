"""System module API schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from nextfight.core.config import Environment


class HealthResponse(BaseModel):
    """Public operational health response."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["healthy"]
    environment: Environment
    version: str
    dependencies: dict[str, Literal["healthy", "unhealthy"]] | None = None
