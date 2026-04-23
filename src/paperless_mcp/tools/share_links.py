"""MCP tool registrations for share links (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.share_link import ShareLink
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register share link tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_share_links", read_only_mode=read_only)
    async def list_share_links(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = 100,
        document_id: int | None = None,
    ) -> Paginated[ShareLink]:
        """List share links (optionally filtered by document)."""
        return await client.share_links.list(
            page=page, page_size=page_size, document_id=document_id
        )

    @register_tool(mcp, "get_share_link", read_only_mode=read_only)
    async def get_share_link(share_link_id: int) -> ShareLink:
        """Fetch a share link by ID."""
        return await client.share_links.get(share_link_id)
