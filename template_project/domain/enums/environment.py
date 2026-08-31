"""Deployment environments the service runs in."""

from enum import Enum


class Environment(str, Enum):
    """Named deployment targets.

    Attributes
    ----------
    LOCAL : str
        ``"local"`` — developer machine, secrets read from ``.env``.
    DEV : str
        ``"dev"`` — shared development environment.
    TEST : str
        ``"test"`` — automated test environment.
    PROD : str
        ``"prod"`` — production.
    """

    LOCAL: str = "local"
    DEV: str = "dev"
    TEST: str = "test"
    PROD: str = "prod"
