"""Domain-layer re-exports for paperless-mcp consumers.

Importers that need a typed Paperless client can do::

    from paperless_mcp.domain import PaperlessClient

instead of reaching into ``paperless_mcp.client`` directly.
"""

from __future__ import annotations

from paperless_mcp.client import (
    AuthError,
    ConflictError,
    NotFoundError,
    PaperlessAPIError,
    PaperlessClient,
    RateLimitError,
    UpstreamError,
    ValidationError,
)

__all__ = [
    "AuthError",
    "ConflictError",
    "NotFoundError",
    "PaperlessAPIError",
    "PaperlessClient",
    "RateLimitError",
    "UpstreamError",
    "ValidationError",
]
