"""Async HTTP client shared by every outbound REST integration."""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx


class RestClient:
    """Thin async wrapper over :class:`httpx.AsyncClient`.

    Parameters
    ----------
    base_url : str
        Root URL every relative path is resolved against.
    api_key : str | None, optional
        Bearer token sent with every request when set.
    default_headers : dict[str, str] | None, optional
        Headers merged into every request.
    timeout : float, optional
        Per-request timeout in seconds, used when no client is injected.
    client : httpx.AsyncClient | None, optional
        Client to reuse; a private one is created and owned when omitted.
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        default_headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._default_headers = default_headers or {}
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)

    def _build_url(self, path: str) -> str:
        """Resolve ``path`` against the configured base URL.

        Parameters
        ----------
        path : str
            Absolute URL or path relative to the base URL.

        Returns
        -------
        str
            The URL to request.
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self._base_url}/{path.lstrip('/')}"

    def _authorized_headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        """Merge default headers, the bearer token and per-call headers.

        Parameters
        ----------
        headers : dict[str, str] | None
            Headers supplied for a single call.

        Returns
        -------
        dict[str, str]
            The headers to send.
        """
        merged = dict(self._default_headers)
        if self._api_key:
            merged["Authorization"] = f"Bearer {self._api_key}"
        merged.update(headers or {})
        return merged

    async def request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        auto_raise: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a request and optionally raise on an error status.

        Parameters
        ----------
        method : str
            HTTP verb.
        path : str
            Absolute URL or path relative to the base URL.
        headers : dict[str, str] | None, optional
            Headers for this call only.
        auto_raise : bool, optional
            Raise on 4xx/5xx responses instead of returning them.
        **kwargs : Any
            Extra arguments forwarded to :meth:`httpx.AsyncClient.request`.

        Returns
        -------
        httpx.Response
            The response.

        Raises
        ------
        httpx.HTTPStatusError
            If ``auto_raise`` is set and the status is 4xx or 5xx; the message
            carries the response body, which the httpx error omits.
        """
        response = await self._client.request(
            method,
            self._build_url(path),
            headers=self._authorized_headers(headers),
            **kwargs,
        )
        if auto_raise:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as error:
                raise httpx.HTTPStatusError(
                    f"{error}. Response body: {response.text}",
                    request=error.request,
                    response=error.response,
                ) from error
        return response

    async def get(self, *, path: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request. See :meth:`request` for the parameters."""
        return await self.request(method="GET", path=path, **kwargs)

    async def post(self, *, path: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request. See :meth:`request` for the parameters."""
        return await self.request(method="POST", path=path, **kwargs)

    async def put(self, *, path: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request. See :meth:`request` for the parameters."""
        return await self.request(method="PUT", path=path, **kwargs)

    async def delete(self, *, path: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request. See :meth:`request` for the parameters."""
        return await self.request(method="DELETE", path=path, **kwargs)

    async def aclose(self) -> None:
        """Close the underlying client when this instance created it."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> RestClient:
        """Return the client itself so it can be used as a context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the client on context exit."""
        await self.aclose()
