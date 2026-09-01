"""Outbound DTOs describing failures."""

from pydantic import Field

from template_project.presentation.response_models.base.base_response_model import (
    BaseResponseModel,
)


class ValidationErrorResponse(BaseResponseModel):
    """Body of a 400 response."""

    errors: list[str] = Field(..., alias="Errors", description="Validation failures.")


class ErrorResponse(BaseResponseModel):
    """Body of any response whose failure is a single message, such as 401 or 404."""

    error: str = Field(..., alias="Error", description="Why the request was rejected.")


class DetailedErrorResponse(BaseResponseModel):
    """Body of a 500 response, mirroring :class:`APIException`."""

    type: str = Field(..., alias="Type", description="URI describing the status.")
    title: str = Field(..., alias="Title", description="Short summary.")
    detail: str = Field(..., alias="Detail", description="What went wrong.")
    error_code: str = Field(..., alias="ErrorCode", description="Error identifier.")
    severity: str = Field(..., alias="Severity", description="Impact on the caller.")
