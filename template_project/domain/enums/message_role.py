"""Roles a conversation turn can be attributed to."""

from enum import Enum


class MessageRole(str, Enum):
    """Author of a conversation turn.

    Attributes
    ----------
    USER : str
        ``"user"`` — the human side of the conversation.
    ASSISTANT : str
        ``"assistant"`` — the model side of the conversation.
    """

    USER: str = "user"
    ASSISTANT: str = "assistant"
