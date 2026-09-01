"""Base exception for every failure the API reports to a caller."""

from template_project.domain.enums.api_error_code import APIErrorCode


class APIException(Exception):
    """Domain failure carrying everything an error response needs."""

    def __init__(
        self,
        error_code: APIErrorCode = APIErrorCode.API_ERROR,
        title: str = "Internal Server Error",
        detail: str = "An unexpected error occurred.",
        type: str = "https://httpstatuses.com/500",
    ) -> None:
        self.error_code = error_code
        self.title = title
        self.detail = detail
        self.type = type
        super().__init__(self.detail)
