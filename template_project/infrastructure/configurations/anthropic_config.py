"""Configuration for the Anthropic language model."""

from pydantic import BaseModel, Field


class AnthropicConfig(BaseModel):
    """Model selection and sampling behaviour for completions.

    Attributes
    ----------
    model : str
        Model identifier; larger models cost more and answer slower.
    max_tokens : int
        Upper bound on answer length. Raising it raises worst-case latency.
    temperature : float
        Sampling randomness; 0 is deterministic, 1 is most varied.
    timeout_seconds : float
        How long a single call may take before it is abandoned.
    max_retries : int
        Retries the SDK performs on transient failures.
    system_prompt : str
        Instructions prepended to every conversation.
    """

    model: str = Field("claude-sonnet-4-6", description="Model identifier.")
    max_tokens: int = Field(4096, ge=1, le=64000, description="Answer length cap.")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling randomness.")
    timeout_seconds: float = Field(
        60.0, gt=0.0, le=600.0, description="Per-call timeout in seconds."
    )
    max_retries: int = Field(2, ge=0, le=10, description="SDK retries on failure.")
    system_prompt: str = Field(
        "You are a helpful assistant.",
        description="Instructions prepended to every conversation.",
    )
