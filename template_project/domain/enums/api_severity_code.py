"""Severity levels attached to API errors."""

from enum import Enum


class APISeverityCode(str, Enum):
    """How badly a failure affects the caller."""

    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"
