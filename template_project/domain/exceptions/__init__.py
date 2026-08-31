"""Domain exceptions."""

from template_project.domain.exceptions.api_exception import APIException
from template_project.domain.exceptions.authentication_exception import (
    AuthenticationException,
)
from template_project.domain.exceptions.validation_exception import ValidationException

__all__ = ["APIException", "AuthenticationException", "ValidationException"]
