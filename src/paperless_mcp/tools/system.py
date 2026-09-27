"""MCP tool registrations for system endpoints (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

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
    @tool_boundary
    @paperless_errors
    async def get_statistics() -> Statistics:
        """Get counts for the whole archive: documents, inbox documents, tags, correspondents, types, characters and file types."""
        return await client.system.statistics()

    @mcp.tool(**tool_metadata("get_remote_version"))
    @tool_boundary
    @paperless_errors
    async def get_remote_version() -> RemoteVersion:
        """Check whether a newer Paperless-NGX release exists; returns the newest release.

        That is the newest release published upstream, not the version
        installed on this instance, with a flag saying whether it is newer.
        Use get_server_info for the installed version.
        """
        return await client.system.remote_version()
