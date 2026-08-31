"""Machine-readable error codes returned to API clients."""

from enum import Enum


class APIErrorCode(str, Enum):
    """Stable error identifiers carried by every :class:`APIException`.

    Attributes
    ----------
    API_ERROR : str
        ``"api/error"`` — unclassified server-side failure.
    AUTHENTICATION_ERROR : str
        ``"api/authentication-error"`` — the caller is unknown or unauthorised.
    VALIDATION_ERROR : str
        ``"api/validation-error"`` — the request payload failed validation.
    """

    API_ERROR: str = "api/error"
    AUTHENTICATION_ERROR: str = "api/authentication-error"
    VALIDATION_ERROR: str = "api/validation-error"
