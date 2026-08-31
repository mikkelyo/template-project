"""HTTP client for the example downstream API."""

from __future__ import annotations

from typing import Any

import httpx

from template_project.infrastructure.clients.base.rest_client import RestClient
from template_project.infrastructure.configurations.example_api_config import (
    ExampleApiConfig,
)


class ExampleClient(RestClient):
    """Calls the example downstream API and returns plain Python data.

    Parameters
    ----------
    base_url : str
        Root URL of the API.
    timeout : float
        Per-request timeout in seconds.
    client : httpx.AsyncClient | None, optional
        Client to reuse; a private one is created when omitted.
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(base_url=base_url, timeout=timeout, client=client)

    async def fetch_item(self, *, item_id: str) -> dict[str, Any]:
        """Read a single item.

        Parameters
        ----------
        item_id : str
            Identifier of the item.

        Returns
        -------
        dict[str, Any]
            The decoded item.
        """
        response = await self.get(path=f"/items/{item_id}")
        item: dict[str, Any] = response.json()
        return item


def create_example_client(*, config: ExampleApiConfig) -> ExampleClient:
    """Build an :class:`ExampleClient` from its configuration.

    Parameters
    ----------
    config : ExampleApiConfig
        Connection settings for the API.

    Returns
    -------
    ExampleClient
        A ready-to-use client.
    """
    return ExampleClient(base_url=config.base_url, timeout=config.timeout_seconds)
