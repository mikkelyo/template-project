"""LLM configuration."""

from pydantic import BaseModel


class LLMConfig(BaseModel):
    api_key: str = ""
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    temperature: float = 0.7
