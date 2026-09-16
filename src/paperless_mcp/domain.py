"""Domain layer for paperless-mcp: the Paperless client lifecycle and re-exports.

The template's ``_server_deps.server_lifespan`` (template-owned) constructs a
:class:`Service` here on startup and stops it on shutdown.  Tool and resource
registration happens before the lifespan runs, so the shared
:class:`~paperless_mcp.tools._context.ToolContext` is built eagerly at
registration time and staged in a module-level slot; :meth:`Service.start`
adopts it so :meth:`Service.stop` can close the HTTP client.

:func:`tool_context_for` keys that slot on the server it was built for, so
``register_tools`` and ``register_resources`` share one client whichever of
them runs first.  The order is decided in template-owned ``server.py``, which
a ``copier update`` re-renders, so it is not an invariant this package can
rely on.

The slot holds one entry.  Staging a second server's context over an
unadopted first closes the first one's client on the way out, so a process
that builds servers it never enters — a test suite, mostly — does not
accumulate them.

Importers that need a typed Paperless client can do::

    from paperless_mcp.domain import PaperlessClient

instead of reaching into ``paperless_mcp.client`` directly.
"""

from __future__ import annotations

import asyncio
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
    "pending_tool_context",
    "tool_context_for",
]

_pending: tuple[object, ToolContext] | None = None


def tool_context_for(mcp: object) -> ToolContext:
    """Return the shared :class:`ToolContext` for *mcp*, building it once.

    The first registrar to ask builds the Paperless client and stages the
    context against *mcp*; the second gets the same object back rather than
    opening a second HTTP client. Staging is what lets :class:`Service`, which
    the lifespan constructs long after registration, close that client.

    Args:
        mcp: The server being registered on, used only as an identity so a
            second server does not adopt the first one's client.

    Returns:
        The context for *mcp*, freshly built or the already-staged one.
    """
    from paperless_mcp._domain_config import load_domain_config
    from paperless_mcp.tools._context import ToolContext

    global _pending
    if _pending is not None:
        if _pending[0] is mcp:
            return _pending[1]
        _discard(_pending[1])
        _pending = None

    cfg = load_domain_config()
    client = PaperlessClient(
        base_url=cfg.paperless_url,
        api_token=cfg.api_token.get_secret_value(),
        timeout_seconds=cfg.http_timeout_seconds,
        max_retries=cfg.http_retries,
    )
    context = ToolContext(
        client=client,
        default_page_size=cfg.default_page_size,
        public_url=cfg.public_url,
    )
    _pending = (mcp, context)
    return context


def _discard(context: ToolContext) -> None:
    """Close a staged context that no lifespan will ever adopt.

    Server construction is synchronous — pvl-core finalises the composed
    instructions during it and refuses to do that inside a running loop — so
    there is normally no loop here and the close completes. If there is one,
    closing would mean blocking it, so the client is dropped instead: it opens
    no sockets until its first request, and a context nothing adopted never
    makes one.

    Args:
        context: The staged context being replaced.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(context.client.aclose())
        logger.debug("unadopted_tool_context_closed")
    else:
        logger.debug("unadopted_tool_context_dropped reason=running_event_loop")


def pending_tool_context() -> ToolContext | None:
    """Return the context staged by :func:`tool_context_for`, if any.

    Returns:
        The staged context, or ``None`` when nothing is staged.
    """
    return _pending[1] if _pending is not None else None


class Service:
    """Owns the staged Paperless client for the duration of the server lifespan."""

    def __init__(self) -> None:
        self._ready = False
        self._context: ToolContext | None = None

    async def start(self) -> None:
        """Adopt the staged tool context; the lifespan now owns its client."""
        global _pending
        self._context = pending_tool_context()
        _pending = None
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
