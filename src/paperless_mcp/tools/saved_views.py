"""MCP tool registrations for saved views (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.saved_view import SavedView
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import Page, PageSize


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register saved view tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_saved_views"))
    @tool_boundary
    @paperless_errors
    async def list_saved_views(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
    ) -> Paginated[SavedView]:
        """List saved views, the named document filters users keep in Paperless; returns one page."""
        return await client.saved_views.list(page=page, page_size=page_size)

    @mcp.tool(**tool_metadata("get_saved_view"))
    @tool_boundary
    @paperless_errors
    async def get_saved_view(view_id: int) -> SavedView:
        """Get one saved view by id, with its filter rules and sort order."""
        return await client.saved_views.get(view_id)
