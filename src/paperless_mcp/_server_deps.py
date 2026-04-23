"""Service lifespan + dependency injection for Paperless MCP."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypedDict

from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

logger = logging.getLogger(__name__)


class Service:
    """Template placeholder — starts/stops with the server lifespan."""

    def __init__(self) -> None:
        self._ready = False

    async def start(self) -> None:
        self._ready = True

    async def stop(self) -> None:
        self._ready = False


class LifespanState(TypedDict):
    """Shape of the lifespan context yielded to request handlers."""

    service: Service


@asynccontextmanager
async def server_lifespan(_mcp: object) -> AsyncIterator[dict[str, Any]]:
    """Start the service on startup; stop it on shutdown."""
    service = Service()
    await service.start()
    logger.info("Service started")
    try:
        yield {"service": service}
    finally:
        await service.stop()
        logger.info("Service stopped")


def get_service(ctx: Context = CurrentContext()) -> Service:
    """Resolve the running :class:`Service` from the request context.

    Use as a ``Depends`` default in tool/resource/prompt handlers.

    Raises:
        RuntimeError: If the server lifespan has not run.
    """
    service: Service | None = ctx.lifespan_context.get("service")
    if service is None:
        msg = "Service not initialised — server lifespan has not run"
        raise RuntimeError(msg)
    return service
