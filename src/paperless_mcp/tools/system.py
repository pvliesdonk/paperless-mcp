"""MCP tool registrations for system endpoints (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp.models.system import RemoteVersion, Statistics
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register system tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("get_statistics"))
    @paperless_errors
    async def get_statistics() -> Statistics:
        """Fetch collection-level statistics."""
        return await client.system.statistics()

    @mcp.tool(**tool_metadata("get_remote_version"))
    @paperless_errors
    async def get_remote_version() -> RemoteVersion:
        """Check whether a newer release of Paperless-NGX exists upstream.

        Answers the newest release published on GitHub, and whether it is newer
        than the connected instance -- not the version installed on that
        instance.  The two coincide only while the instance is up to date.
        Call ``get_server_info`` for the installed version.
        """
        return await client.system.remote_version()
