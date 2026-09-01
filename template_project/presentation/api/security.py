"""Authentication dependencies and the composed dependency list routes apply."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from template_project.constants.context_keys import ContextKeys
from template_project.constants.static_messages import StaticMessages
from template_project.context import context
from template_project.domain.exceptions.authentication_exception import (
    AuthenticationException,
)
from template_project.domain.user.current_user import CurrentUser

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """Reject requests that do not carry the configured bearer token."""
    if credentials is None or credentials.credentials != settings.service_api_key:
        raise AuthenticationException(detail=StaticMessages.INVALID_API_KEY)


async def set_current_user_from_body(request: Request) -> None:
    """Bind the caller described in the request body to the request context."""
    body = await request.json()
    user_id = body.get("UserId")
    user_name = body.get("UserName")
    if not user_id or not user_name:
        raise AuthenticationException(detail=StaticMessages.MISSING_CURRENT_USER)
    context.set(
        ContextKeys.CURRENT_USER,
        CurrentUser(user_id=user_id, user_name=user_name),
    )


AUTH_AND_CONTEXT = [Depends(require_api_key), Depends(set_current_user_from_body)]
