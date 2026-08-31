"""The caller a request is executed on behalf of."""

from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    """Identity of the caller behind the current request.

    Attributes
    ----------
    user_id : str
        Stable identifier of the caller.
    user_name : str
        Display name of the caller.
    """

    user_id: str = Field(..., description="Stable identifier of the caller.")
    user_name: str = Field(..., description="Display name of the caller.")
