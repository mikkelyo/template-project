"""Raised when a request payload is structurally valid but semantically wrong."""

from template_project.domain.enums.api_error_code import APIErrorCode
from template_project.domain.enums.api_severity_code import APISeverityCode
from template_project.domain.exceptions.api_exception import APIException


class ValidationException(APIException):
    """A value supplied by the caller is not acceptable.

    Parameters
    ----------
    detail : str, optional
        Explanation of what is wrong with the value.
    field : str | None, optional
        Name of the offending field, when the failure is attributable to one.
    """

    def __init__(
        self,
        detail: str = "The request payload is invalid.",
        field: str | None = None,
    ) -> None:
        self.field = field
        super().__init__(
            error_code=APIErrorCode.VALIDATION_ERROR,
            title="Bad Request",
            detail=detail,
            type="https://httpstatuses.com/400",
            severity=APISeverityCode.LOW,
        )
