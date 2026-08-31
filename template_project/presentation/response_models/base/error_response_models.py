"""Outbound DTOs describing failures."""

from pydantic import Field

from template_project.presentation.response_models.base.base_response_model import (
    BaseResponseModel,
)


class ValidationErrorResponse(BaseResponseModel):
    """Body of a 400 response.

    Attributes
    ----------
    errors : list[str]
        One entry per field that failed validation.
    """

    errors: list[str] = Field(..., alias="Errors", description="Validation failures.")


class UnauthorizedErrorResponse(BaseResponseModel):
    """Body of a 401 response.

    Attributes
    ----------
    error : str
        Why the request was rejected.
    """

    error: str = Field(..., alias="Error", description="Why the request was rejected.")


class DetailedErrorResponse(BaseResponseModel):
    """Body of a 500 response, mirroring :class:`APIException`.

    Attributes
    ----------
    type : str
        URI describing the HTTP status the failure maps to.
    title : str
        Short human-readable summary.
    detail : str
        Explanation of what went wrong.
    error_code : str
        Machine-readable identifier for the failure.
    severity : str
        How badly the failure affects the caller.
    """

    type: str = Field(..., alias="Type", description="URI describing the status.")
    title: str = Field(..., alias="Title", description="Short summary.")
    detail: str = Field(..., alias="Detail", description="What went wrong.")
    error_code: str = Field(..., alias="ErrorCode", description="Error identifier.")
    severity: str = Field(..., alias="Severity", description="Impact on the caller.")
