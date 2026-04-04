"""Anthropic LLM client."""

from anthropic import Anthropic

from template_project.core.configs.llm_config import LLMConfig


class LLMClient:
    """Client for interacting with the Anthropic API."""

    def __init__(self, api_key: str, llm_config: LLMConfig):
        self.client = Anthropic(api_key=api_key)
        self.model = llm_config.model
        self.max_tokens = llm_config.max_tokens
        self.temperature = llm_config.temperature

    def send_message(self, messages: list[dict], **kwargs) -> str:
        """Send messages and return the assistant's text response."""
        response = self.client.messages.create(
            model=kwargs.pop("model", self.model),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            temperature=kwargs.pop("temperature", self.temperature),
            messages=messages,
            **kwargs,
        )
        return response.content[0].text
