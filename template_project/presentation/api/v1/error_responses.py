"""OpenAPI error schemas shared by every v1 route."""

from typing import Any

from template_project.presentation.response_models.base.error_response_models import (
    DetailedErrorResponse,
    ErrorResponse,
    ValidationErrorResponse,
)

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": ValidationErrorResponse, "description": "Invalid request payload."},
    401: {"model": ErrorResponse, "description": "Unauthenticated caller."},
    500: {"model": DetailedErrorResponse, "description": "Unexpected server failure."},
}
