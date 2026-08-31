"""Outcome of a completion request."""

from pydantic import BaseModel, Field


class CompletionResult(BaseModel):
    """What the model answered and who asked for it.

    Attributes
    ----------
    answer : str
        Text produced by the model.
    requested_by : str
        Identifier of the caller the answer was produced for.
    """

    answer: str = Field(..., description="Text produced by the model.")
    requested_by: str = Field(
        ..., description="Identifier of the caller the answer was produced for."
    )
