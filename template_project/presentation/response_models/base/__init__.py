"""Shared response DTO bases."""

from template_project.presentation.response_models.base.base_response_model import (
    BaseResponseModel,
)
from template_project.presentation.response_models.base.error_response_models import (
    DetailedErrorResponse,
    UnauthorizedErrorResponse,
    ValidationErrorResponse,
)

__all__ = [
    "BaseResponseModel",
    "DetailedErrorResponse",
    "UnauthorizedErrorResponse",
    "ValidationErrorResponse",
]
