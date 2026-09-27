"""MCP tool registrations for share links (read-only)."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.share_link import ShareLink
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import Page, PageSize


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register share link tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    def _with_share_url(link: ShareLink) -> None:
        """Populate *link*'s ``share_url`` when a public URL is configured."""
        if ctx.public_url:
            link.share_url = f"{ctx.public_url}/share/{link.slug}"

    @mcp.tool(**tool_metadata("list_share_links"))
    @tool_boundary
    @paperless_errors
    async def list_share_links(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        document_id: int | None = None,
    ) -> Paginated[ShareLink]:
        """List public share links for documents; returns one page with each link's document, expiry and URL.

        Args:
            document_id: Keep only the links to this document.
        """
        result = await client.share_links.list(
            page=page, page_size=page_size, document_id=document_id
        )
        for link in result.results:
            _with_share_url(link)
        return result

    @mcp.tool(**tool_metadata("get_share_link"))
    @tool_boundary
    @paperless_errors
    async def get_share_link(share_link_id: int) -> ShareLink:
        """Get one share link by id, with its document, expiry and URL."""
        link = await client.share_links.get(share_link_id)
        _with_share_url(link)
        return link
