"""MCP tool registrations for saved views (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.saved_view import SavedView
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register saved view tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @register_tool(mcp, "list_saved_views")
    async def list_saved_views(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
    ) -> Paginated[SavedView]:
        """List saved views."""
        return await client.saved_views.list(page=page, page_size=page_size)

    @register_tool(mcp, "get_saved_view")
    async def get_saved_view(view_id: int) -> SavedView:
        """Fetch a saved view by ID."""
        return await client.saved_views.get(view_id)
