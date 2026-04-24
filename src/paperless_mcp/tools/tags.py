"""MCP tool registrations for tags."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.tag import Tag, TagCreate, TagPatch
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register tag tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_tags", read_only_mode=read_only)
    async def list_tags(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[Tag]:
        """List tags."""
        return await client.tags.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @register_tool(mcp, "get_tag", read_only_mode=read_only)
    async def get_tag(tag_id: int) -> Tag:
        """Fetch a tag by ID."""
        return await client.tags.get(tag_id)

    @register_tool(mcp, "create_tag", read_only_mode=read_only)
    async def create_tag(body: TagCreate) -> Tag:
        """Create a new tag."""
        return await client.tags.create(body)

    @register_tool(mcp, "update_tag", read_only_mode=read_only)
    async def update_tag(tag_id: int, patch: TagPatch) -> Tag:
        """Patch selected fields on a tag."""
        return await client.tags.update(tag_id, patch)

    @register_tool(mcp, "delete_tag", read_only_mode=read_only)
    async def delete_tag(tag_id: int) -> None:
        """Delete a tag."""
        await client.tags.delete(tag_id)

    @register_tool(mcp, "bulk_edit_tags", read_only_mode=read_only)
    async def bulk_edit_tags(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of tags."""
        return await client.tags.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
