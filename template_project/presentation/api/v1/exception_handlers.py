"""Maps exceptions to the error DTOs the API contract promises."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from template_project.domain.exceptions.api_exception import APIException
from template_project.domain.exceptions.authentication_exception import (
    AuthenticationException,
)
from template_project.domain.exceptions.validation_exception import ValidationException
from template_project.presentation.response_models.base.error_response_models import (
    DetailedErrorResponse,
    UnauthorizedErrorResponse,
    ValidationErrorResponse,
)


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render a FastAPI payload validation failure as a 400.

    Parameters
    ----------
    request : Request
        The rejected request.
    exc : RequestValidationError
        Failure raised while parsing the payload.

    Returns
    -------
    JSONResponse
        400 carrying one message per offending field.
    """
    errors = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(errors=errors).model_dump(by_alias=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Render a framework-raised HTTP error, such as a rejected token.

    Parameters
    ----------
    request : Request
        The rejected request.
    exc : HTTPException
        Failure raised by a dependency or route.

    Returns
    -------
    JSONResponse
        The exception's own status carrying its detail.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=UnauthorizedErrorResponse(error=str(exc.detail)).model_dump(
            by_alias=True
        ),
    )


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """Render an unidentified caller as a 401.

    Parameters
    ----------
    request : Request
        The rejected request.
    exc : AuthenticationException
        Failure raised while resolving the caller.

    Returns
    -------
    JSONResponse
        401 carrying the reason.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=UnauthorizedErrorResponse(error=exc.detail).model_dump(by_alias=True),
    )


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Render a rejected domain value as a 400.

    Parameters
    ----------
    request : Request
        The rejected request.
    exc : ValidationException
        Failure raised by a use case.

    Returns
    -------
    JSONResponse
        400 naming the offending field when one is known.
    """
    message = f"{exc.field}: {exc.detail}" if exc.field else exc.detail
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ValidationErrorResponse(errors=[message]).model_dump(by_alias=True),
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Render any other domain failure as a 500.

    Parameters
    ----------
    request : Request
        The rejected request.
    exc : APIException
        Failure raised anywhere below the route.

    Returns
    -------
    JSONResponse
        500 carrying the full error description.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=DetailedErrorResponse(
            type=exc.type,
            title=exc.title,
            detail=exc.detail,
            error_code=exc.error_code.value,
            severity=exc.severity.value,
        ).model_dump(by_alias=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every handler above to ``app``.

    Parameters
    ----------
    app : FastAPI
        Application the handlers are registered on.
    """
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationException, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(APIException, api_exception_handler)  # type: ignore[arg-type]
