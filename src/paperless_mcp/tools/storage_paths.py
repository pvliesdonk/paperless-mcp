"""MCP tool registrations for storage paths (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.storage_path import StoragePath
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import Ordering, Page, PageSize


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register storage path tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_storage_paths"))
    @tool_boundary
    @paperless_errors
    async def list_storage_paths(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: Ordering = None,
    ) -> Paginated[StoragePath]:
        """List storage paths, the folder layouts Paperless files documents into; returns one page."""
        return await client.storage_paths.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @mcp.tool(**tool_metadata("get_storage_path"))
    @tool_boundary
    @paperless_errors
    async def get_storage_path(storage_path_id: int) -> StoragePath:
        """Get one storage path by id, with its path template."""
        return await client.storage_paths.get(storage_path_id)
