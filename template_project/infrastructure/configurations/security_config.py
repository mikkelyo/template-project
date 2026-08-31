"""Configuration for inbound request authentication."""

from pydantic import BaseModel, Field


class SecurityConfig(BaseModel):
    """How callers of this service are authenticated.

    Attributes
    ----------
    allowed_origins : list[str]
        Origins accepted by the CORS middleware.
    """

    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"], description="Origins accepted by CORS."
    )
