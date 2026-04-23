"""Tool registrations for Paperless MCP.

Each submodule exposes a ``register(mcp, ctx)`` function.
:func:`register_all` calls every one in order.
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from paperless_mcp._server_deps import get_service
from paperless_mcp.domain import Service

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register all domain tools on *mcp*."""

    @mcp.tool(annotations={"readOnlyHint": True})
    async def ping(service: Service = Depends(get_service)) -> str:
        """Health-check tool — returns ``"pong"`` if the service is alive."""
        return await service.ping()
