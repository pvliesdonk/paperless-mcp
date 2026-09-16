"""Domain layer for paperless-mcp: the Paperless client lifecycle and re-exports.

The template's ``_server_deps.server_lifespan`` (template-owned) constructs a
:class:`Service` here on startup and stops it on shutdown.  Tool and resource
registration happens before the lifespan runs, so the shared
:class:`~paperless_mcp.tools._context.ToolContext` is built eagerly at
registration time and staged in a module-level slot; :meth:`Service.start`
adopts it so :meth:`Service.stop` can close the HTTP client.

The staging slot is process-global, so two servers constructed before either
lifespan starts would share one staged context.  Construct and enter servers
pairwise (the way ``Client(make_server())`` does) and that cannot happen.

Importers that need a typed Paperless client can do::

    from paperless_mcp.domain import PaperlessClient

instead of reaching into ``paperless_mcp.client`` directly.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from paperless_mcp.tools._context import ToolContext

logger = logging.getLogger(__name__)

__all__ = [
    "AuthError",
    "ConflictError",
    "NotFoundError",
    "PaperlessAPIError",
    "PaperlessClient",
    "RateLimitError",
    "Service",
    "UpstreamError",
    "ValidationError",
    "build_tool_context",
    "pending_tool_context",
]

_pending_context: ToolContext | None = None


def build_tool_context() -> ToolContext:
    """Build the shared :class:`ToolContext` from env and stage it for the lifespan.

    Called once per server construction by
    :func:`~paperless_mcp.tools.register_tools`; a following
    :func:`~paperless_mcp.resources.register_resources` reuses the staged
    context instead of opening a second HTTP client.

    Returns:
        The freshly built context, which is also the staged one.
    """
    from paperless_mcp._domain_config import load_domain_config
    from paperless_mcp.tools._context import ToolContext

    global _pending_context
    cfg = load_domain_config()
    client = PaperlessClient(
        base_url=cfg.paperless_url,
        api_token=cfg.api_token.get_secret_value(),
        timeout_seconds=cfg.http_timeout_seconds,
        max_retries=cfg.http_retries,
    )
    _pending_context = ToolContext(
        client=client,
        default_page_size=cfg.default_page_size,
        public_url=cfg.public_url,
    )
    return _pending_context


def pending_tool_context() -> ToolContext | None:
    """Return the context staged by :func:`build_tool_context`, if any.

    Returns:
        The staged context, or ``None`` when nothing is staged.
    """
    return _pending_context


class Service:
    """Owns the staged Paperless client for the duration of the server lifespan."""

    def __init__(self) -> None:
        self._ready = False
        self._context: ToolContext | None = None

    async def start(self) -> None:
        """Adopt the staged tool context; the lifespan now owns its client."""
        global _pending_context
        self._context = _pending_context
        _pending_context = None
        self._ready = True

    async def stop(self) -> None:
        """Close the Paperless HTTP client this service adopted."""
        if self._context is not None:
            await self._context.client.aclose()
            logger.info("client_closed")
        self._context = None
        self._ready = False

    async def ping(self) -> str:
        """Answer a liveness probe.

        Returns:
            ``"pong"`` once the lifespan has started, ``"not ready"`` before.
        """
        return "pong" if self._ready else "not ready"

    async def status(self) -> dict[str, object]:
        """Report the service's readiness.

        Returns:
            A mapping with a single ``ready`` key.
        """
        return {"ready": self._ready}
