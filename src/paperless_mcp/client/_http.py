"""HTTP base for the Paperless-NGX client.

All resource clients (``documents.py``, ``tags.py``, ...) go through
:class:`PaperlessHTTP` for authenticated requests, retry on transient
errors, and consistent error mapping.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

from paperless_mcp.client._errors import PaperlessAPIError, error_from_response

logger = logging.getLogger(__name__)

_ACCEPT_HEADER = "application/json; version=9"
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

_SECRET_HEADER_RE = re.compile(
    r"(Authorization['\"]?\s*[:=]\s*['\"]?)(Token|Bearer)\s+[^\s'\"]+",
    re.IGNORECASE,
)


class _SecretMaskFilter(logging.Filter):
    """Redact ``Authorization: Token …`` and ``Bearer …`` from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            original = record.getMessage()
        except Exception:  # pragma: no cover - defensive
            return True
        masked = _SECRET_HEADER_RE.sub(r"\1\2 ***", original)
        if masked != original:
            record.msg = masked
            record.args = ()
        return True


logger.addFilter(_SecretMaskFilter())


class PaperlessHTTP:
    """Async HTTP client wrapping :class:`httpx.AsyncClient` for Paperless-NGX.

    The client is single-session: construct once per process, reuse across
    requests.  Call :meth:`aclose` on shutdown.
    """

    def __init__(
        self,
        base_url: str,
        api_token: str,
        *,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
    ) -> None:
        if max_retries < 0:
            msg = "max_retries must be >= 0"
            raise ValueError(msg)
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout_seconds),
            headers={
                "Authorization": f"Token {api_token}",
                "Accept": _ACCEPT_HEADER,
            },
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return await self._request_json("GET", path, params=params)

    async def post_json(
        self,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return await self._request_json("POST", path, json=json, params=params)

    async def patch_json(self, path: str, *, json: Any | None = None) -> Any:
        return await self._request_json("PATCH", path, json=json)

    async def delete(self, path: str) -> None:
        await self._request("DELETE", path)

    async def stream_bytes(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> tuple[bytes, str]:
        """Fetch a raw binary resource (thumbnail, preview, download)."""
        response = await self._request("GET", path, params=params)
        return response.content, response.headers.get(
            "content-type", "application/octet-stream"
        )

    async def paginate(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[Any]:
        """Walk a paginated Paperless list endpoint yielding each result.

        Args:
            path: API path (e.g. ``/api/tags/``).
            params: Initial query parameters.  ``page_size=100`` is added
                automatically unless already set.
            limit: Stop after yielding this many items.  ``None`` means walk
                the full list.

        Yields:
            Each ``results`` entry, across however many pages are needed.
        """
        effective_params: dict[str, Any] = dict(params or {})
        effective_params.setdefault("page_size", 100)
        next_path: str | None = path
        next_params: dict[str, Any] | None = effective_params
        yielded = 0
        while next_path is not None:
            body = await self.get_json(next_path, params=next_params)
            for item in body.get("results") or []:
                if limit is not None and yielded >= limit:
                    return
                yield item
                yielded += 1
            next_url = body.get("next")
            if not next_url:
                next_path = None
                continue
            parsed = urlparse(next_url)
            next_path = parsed.path
            next_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._request(method, path, json=json, params=params)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            try:
                response = await self._client.request(
                    method, path, json=json, params=params
                )
            except httpx.RequestError as exc:
                if method in _IDEMPOTENT_METHODS and attempt < self._max_retries:
                    await self._sleep_backoff(attempt)
                    attempt += 1
                    continue
                raise PaperlessAPIError(0, f"network error: {exc}") from exc

            if response.is_success:
                return response

            error = error_from_response(response)
            if (
                error.is_retryable()
                and method in _IDEMPOTENT_METHODS
                and attempt < self._max_retries
                # TODO: respect Retry-After header when present
            ):
                logger.debug(
                    "retryable %s on %s %s (attempt %d/%d)",
                    response.status_code,
                    method,
                    path,
                    attempt + 1,
                    self._max_retries + 1,
                )
                await self._sleep_backoff(attempt)
                attempt += 1
                continue
            raise error

    async def _sleep_backoff(self, attempt: int) -> None:
        delay = self._backoff_factor * (2**attempt)
        await asyncio.sleep(delay)
