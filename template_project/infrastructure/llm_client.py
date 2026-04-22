"""Anthropic LLM client."""

from typing import TypeVar

from anthropic import Anthropic

from template_project.core.configs.llm_config import LLMConfig
from template_project.core.schema import LLMSchema

T = TypeVar("T", bound=LLMSchema)


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

    def use_tool(
        self,
        messages: list[dict],
        tool: type[T],
        description: str,
        **kwargs,
    ) -> T:
        """Force the model to call `tool` and return the validated result."""
        response = self.client.messages.create(
            model=kwargs.pop("model", self.model),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            temperature=kwargs.pop("temperature", self.temperature),
            messages=messages,
            tools=[tool.as_tool(description)],
            tool_choice={"type": "tool", "name": tool.__name__},
            **kwargs,
        )
        block = next(b for b in response.content if b.type == "tool_use")
        return tool.model_validate(block.input)
