"""Inbound DTO for the completion endpoint."""

from pydantic import Field

from template_project.presentation.request_models.base.base_request_model import (
    BaseRequestModel,
)


class CompletionRequestModel(BaseRequestModel):
    """Body of ``POST /v1/completions``.

    Attributes
    ----------
    prompt : str
        Question the caller wants answered.
    user_id : str
        Identifier of the caller, also used to populate the request context.
    user_name : str
        Display name of the caller.
    """

    prompt: str = Field(..., alias="Prompt", description="Question to answer.")
    user_id: str = Field(..., alias="UserId", description="Identifier of the caller.")
    user_name: str = Field(..., alias="UserName", description="Name of the caller.")
