"""Schemas for structured LLM tool-use outputs."""

from pydantic import BaseModel


class LLMSchema(BaseModel):
    """Base for pydantic models exposed to the LLM as forced tool calls."""

    @classmethod
    def as_tool(cls, description: str) -> dict:
        return {
            "name": cls.__name__,
            "description": description,
            "input_schema": cls.model_json_schema(),
        }
