"""Typed exception hierarchy for Paperless-NGX HTTP errors."""

from __future__ import annotations

import json
from typing import Any

import httpx


class PaperlessAPIError(Exception):
    """Base class for every Paperless API error.

    Attributes:
        status_code: HTTP status from the response (or 0 for network errors).
        detail: Server-provided error message, best-effort extracted.
        body: Raw response body (parsed JSON or string), for diagnostics.
    """

    def __init__(self, status_code: int, detail: str, body: Any | None = None) -> None:
        super().__init__(f"[{status_code}] {detail}")
        self.status_code = status_code
        self.detail = detail
        self.body = body

    def is_retryable(self) -> bool:
        """Return ``True`` for errors that are safe to retry on idempotent requests."""
        return False


class ValidationError(PaperlessAPIError):
    """Server rejected the request body (HTTP 400)."""


class AuthError(PaperlessAPIError):
    """Authentication or authorisation failed (HTTP 401/403)."""


class NotFoundError(PaperlessAPIError):
    """Requested entity does not exist (HTTP 404)."""


class ConflictError(PaperlessAPIError):
    """Request conflicts with current state (HTTP 409)."""


class RateLimitError(PaperlessAPIError):
    """Rate limit exceeded (HTTP 429)."""

    def is_retryable(self) -> bool:
        return True


class UpstreamError(PaperlessAPIError):
    """Server-side failure (HTTP 5xx)."""

    def is_retryable(self) -> bool:
        return True


_STATUS_MAP: dict[int, type[PaperlessAPIError]] = {
    400: ValidationError,
    401: AuthError,
    403: AuthError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def _extract_detail(response: httpx.Response) -> tuple[str, Any | None]:
    """Pull a human-readable error message out of a Paperless response."""
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            body = response.json()
        except json.JSONDecodeError:
            return response.text or f"HTTP {response.status_code}", None
        if isinstance(body, dict):
            detail = body.get("detail")
            if detail:
                return str(detail), body
            return json.dumps(body), body
        return str(body), body
    text = response.text.strip()
    return (text or f"HTTP {response.status_code}"), None


def error_from_response(response: httpx.Response) -> PaperlessAPIError:
    """Map an :class:`httpx.Response` to the right :class:`PaperlessAPIError` subclass."""
    detail, body = _extract_detail(response)
    status = response.status_code
    cls = _STATUS_MAP.get(status)
    if cls is not None:
        return cls(status, detail, body)
    if 500 <= status < 600:
        return UpstreamError(status, detail, body)
    return PaperlessAPIError(status, detail, body)
