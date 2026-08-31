"""Anthropic-backed implementation of the completion port."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar

from anthropic import AnthropicError, AsyncAnthropic
from anthropic.types import MessageParam, MetadataParam, ToolChoiceToolParam, ToolParam
from pydantic import BaseModel

from template_project.constants.static_messages import StaticMessages
from template_project.domain.enums.message_role import MessageRole
from template_project.domain.exceptions.api_exception import APIException

if TYPE_CHECKING:
    from collections.abc import Sequence
    from logging import Logger

    from template_project.application.ports.current_user_port import CurrentUserPort
    from template_project.domain.conversation.message import Message

SchemaT = TypeVar("SchemaT", bound=BaseModel)

# Roles are translated explicitly, so a new domain role cannot silently reach the SDK.
VENDOR_ROLES: dict[MessageRole, Literal["user", "assistant"]] = {
    MessageRole.USER: "user",
    MessageRole.ASSISTANT: "assistant",
}


class AnthropicCompletionAdapter:
    """Implements :class:`CompletionPort`, so the Anthropic SDK stays in this layer.

    Parameters
    ----------
    client : AsyncAnthropic
        SDK client used for every call; async so the event loop is never blocked.
    logger : Logger
        Logger for operational messages.
    current_user : CurrentUserPort
        Caller the request is attributed to, for Anthropic's abuse tracking.
    model : str
        Model identifier requests are sent to.
    max_tokens : int
        Upper bound on answer length.
    temperature : float
        Sampling randomness.
    """

    def __init__(
        self,
        *,
        client: AsyncAnthropic,
        logger: Logger,
        current_user: CurrentUserPort,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> None:
        self._client = client
        self._logger = logger
        self._current_user = current_user
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    async def complete(self, *, messages: Sequence[Message], system: str) -> str:
        """Answer a conversation with free-form text.

        Parameters
        ----------
        messages : Sequence[Message]
            Conversation turns in chronological order.
        system : str
            Instructions that frame the whole conversation.

        Returns
        -------
        str
            The model's answer.

        Raises
        ------
        APIException
            If the call failed or the model returned no text block; vendor errors
            never leave this layer.
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                system=system,
                messages=self._to_vendor_messages(messages),
                metadata=self._caller_metadata(),
            )
        except AnthropicError as error:
            self._logger.error("Anthropic rejected the completion: %s", error)
            raise APIException(detail=StaticMessages.COMPLETION_FAILED) from error
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            self._logger.error("Anthropic returned no text block for %s.", self._model)
            raise APIException(detail=StaticMessages.COMPLETION_FAILED)
        return text

    async def complete_structured(
        self,
        *,
        messages: Sequence[Message],
        schema: type[SchemaT],
        description: str,
    ) -> SchemaT:
        """Answer a conversation with an instance of ``schema``.

        Parameters
        ----------
        messages : Sequence[Message]
            Conversation turns in chronological order.
        schema : type[SchemaT]
            Model the answer is validated against, exposed as a forced tool call.
        description : str
            What the model should put into the schema.

        Returns
        -------
        SchemaT
            The validated answer.

        Raises
        ------
        APIException
            If the call failed or the model returned no tool call; vendor errors
            never leave this layer.
        """
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                messages=self._to_vendor_messages(messages),
                tools=[self._to_vendor_tool(schema=schema, description=description)],
                tool_choice=ToolChoiceToolParam(type="tool", name=schema.__name__),
                metadata=self._caller_metadata(),
            )
        except AnthropicError as error:
            self._logger.error("Anthropic rejected the tool call: %s", error)
            raise APIException(detail=StaticMessages.COMPLETION_FAILED) from error
        block = next((b for b in response.content if b.type == "tool_use"), None)
        if block is None:
            self._logger.error(
                "Anthropic returned no tool call for %s.", schema.__name__
            )
            raise APIException(detail=StaticMessages.COMPLETION_FAILED)
        return schema.model_validate(block.input)

    def _caller_metadata(self) -> MetadataParam:
        """Attribute the call to the current caller.

        Returns
        -------
        MetadataParam
            The ``metadata`` payload Anthropic uses for abuse tracking.
        """
        return MetadataParam(user_id=self._current_user.get_current_user().user_id)

    @staticmethod
    def _to_vendor_messages(messages: Sequence[Message]) -> list[MessageParam]:
        """Convert domain turns into the SDK's message payload.

        Parameters
        ----------
        messages : Sequence[Message]
            Conversation turns in chronological order.

        Returns
        -------
        list[MessageParam]
            Payload accepted by the SDK.
        """
        return [
            MessageParam(role=VENDOR_ROLES[m.role], content=m.content) for m in messages
        ]

    @staticmethod
    def _to_vendor_tool(*, schema: type[BaseModel], description: str) -> ToolParam:
        """Expose ``schema`` as a tool definition the model must call.

        Parameters
        ----------
        schema : type[BaseModel]
            Model describing the expected answer.
        description : str
            What the model should put into the schema.

        Returns
        -------
        ToolParam
            Tool definition accepted by the SDK.
        """
        return ToolParam(
            name=schema.__name__,
            description=description,
            input_schema=schema.model_json_schema(),
        )
