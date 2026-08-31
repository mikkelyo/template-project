"""Annotated string types that interpolate the deployment environment name."""

import os
from typing import Annotated

from pydantic import BeforeValidator

from template_project.domain.enums.environment import Environment

ENV_NAME_PLACEHOLDER = "{env_name}"
ENV_NAME_VARIABLE = "APP_ENV_NAME"


def _env_name() -> str:
    """Return the environment name the process runs under.

    Returns
    -------
    str
        Value of ``APP_ENV_NAME``, defaulting to :attr:`Environment.LOCAL`.
    """
    return os.getenv(ENV_NAME_VARIABLE, Environment.LOCAL.value)


def infix_insert_env_name(value: str) -> str:
    """Replace every ``{env_name}`` placeholder in ``value``.

    Parameters
    ----------
    value : str
        Configured string containing the placeholder.

    Returns
    -------
    str
        ``value`` with the environment name interpolated.

    Raises
    ------
    ValueError
        If ``value`` carries no placeholder.
    """
    if ENV_NAME_PLACEHOLDER not in value:
        raise ValueError(
            f"'{value}' must contain the {ENV_NAME_PLACEHOLDER} placeholder."
        )
    return value.replace(ENV_NAME_PLACEHOLDER, _env_name())


def prefix_insert_env_name(value: str) -> str:
    """Replace a leading ``{env_name}`` placeholder in ``value``.

    Parameters
    ----------
    value : str
        Configured string starting with the placeholder.

    Returns
    -------
    str
        ``value`` with the environment name interpolated.

    Raises
    ------
    ValueError
        If ``value`` does not start with the placeholder.
    """
    if not value.startswith(ENV_NAME_PLACEHOLDER):
        raise ValueError(
            f"'{value}' must start with the {ENV_NAME_PLACEHOLDER} placeholder."
        )
    return value.replace(ENV_NAME_PLACEHOLDER, _env_name(), 1)


InfixEnvNameString = Annotated[str, BeforeValidator(infix_insert_env_name)]
PrefixEnvNameString = Annotated[str, BeforeValidator(prefix_insert_env_name)]
