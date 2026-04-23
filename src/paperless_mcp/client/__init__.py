"""Paperless-NGX REST client.

Public API:
    PaperlessClient — facade aggregating resource clients.
    PaperlessAPIError and subclasses — typed exceptions.
"""

from __future__ import annotations

from paperless_mcp.client._errors import (
    AuthError,
    ConflictError,
    NotFoundError,
    PaperlessAPIError,
    RateLimitError,
    UpstreamError,
    ValidationError,
)

__all__ = [
    "AuthError",
    "ConflictError",
    "NotFoundError",
    "PaperlessAPIError",
    "RateLimitError",
    "UpstreamError",
    "ValidationError",
]
