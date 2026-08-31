"""Template project package; exposes the composed dependency container.

The container is resolved on first attribute access rather than at import time:
``config`` imports this package's configuration models, and the container imports
``config``, so an eager re-export would make the two modules import each other.
Callers still write ``from template_project import container``.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from template_project.di_container import Container

__all__ = ["container"]


def __getattr__(name: str) -> "Container":
    """Return the container, importing the composition root on first access.

    Parameters
    ----------
    name : str
        Attribute being read from the package.

    Returns
    -------
    Container
        The composed root container.

    Raises
    ------
    AttributeError
        If any other attribute is requested.
    """
    if name != "container":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from template_project.di_container import container

    return container
