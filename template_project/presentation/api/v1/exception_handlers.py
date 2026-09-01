"""Maps exceptions to the error DTOs the API contract promises."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Starlette raises its own HTTPException for unmatched routes; FastAPI's subclasses it,
# so handling the base class covers both.
from starlette.exceptions import HTTPException

from template_project.domain.exceptions.api_exception import APIException
from template_project.domain.exceptions.authentication_exception import (
    AuthenticationException,
)
from template_project.domain.exceptions.validation_exception import ValidationException
from template_project.presentation.response_models.base.error_response_models import (
    DetailedErrorResponse,
    ErrorResponse,
    ValidationErrorResponse,
)


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render a FastAPI payload validation failure as a 400."""
    errors = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(errors=errors).model_dump(by_alias=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Render any framework-raised HTTP error, keeping the status it carries."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=str(exc.detail)).model_dump(by_alias=True),
    )


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """Render an unidentified caller as a 401."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ErrorResponse(error=exc.detail).model_dump(by_alias=True),
    )


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Render a rejected domain value as a 400."""
    message = f"{exc.field}: {exc.detail}" if exc.field else exc.detail
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(errors=[message]).model_dump(by_alias=True),
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Render any other domain failure as a 500."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=DetailedErrorResponse(
            type=exc.type,
            title=exc.title,
            detail=exc.detail,
            error_code=exc.error_code.value,
        ).model_dump(by_alias=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every handler above to ``app``."""
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationException, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(APIException, api_exception_handler)  # type: ignore[arg-type]
