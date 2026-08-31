"""Severity levels attached to API errors."""

from enum import Enum


class APISeverityCode(str, Enum):
    """How badly a failure affects the caller.

    Attributes
    ----------
    LOW : str
        ``"low"`` — the caller can recover by fixing the request.
    MEDIUM : str
        ``"medium"`` — degraded behaviour, the request may succeed on retry.
    HIGH : str
        ``"high"`` — the request cannot be served and needs operator attention.
    """

    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"
