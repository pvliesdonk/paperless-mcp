"""MCP tool registrations for system endpoints (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp.models.system import RemoteVersion, Statistics
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register system tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @register_tool(mcp, "get_statistics")
    async def get_statistics() -> Statistics:
        """Fetch collection-level statistics."""
        return await client.system.statistics()

    @register_tool(mcp, "get_remote_version")
    async def get_remote_version() -> RemoteVersion:
        """Fetch Paperless version info."""
        return await client.system.remote_version()
