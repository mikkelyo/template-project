"""Configuration for the example downstream REST API."""

from pydantic import BaseModel, Field

from template_project.infrastructure.configurations.base.env_string_validators import (
    InfixEnvNameString,
)


class ExampleApiConfig(BaseModel):
    """Connection settings for the downstream API the service calls.

    Attributes
    ----------
    base_url : InfixEnvNameString
        Root URL; ``{env_name}`` is replaced with the deployment environment.
    timeout_seconds : float
        Per-request timeout; keep it below the caller's own timeout.
    max_retries : int
        Retries on connection errors before the call is reported as failed.
    """

    base_url: InfixEnvNameString = Field(
        "https://api.{env_name}.example.com",
        validate_default=True,
        description="Root URL of the API.",
    )
    timeout_seconds: float = Field(
        10.0, gt=0.0, le=120.0, description="Per-request timeout in seconds."
    )
    max_retries: int = Field(
        2, ge=0, le=10, description="Retries on connection errors."
    )
