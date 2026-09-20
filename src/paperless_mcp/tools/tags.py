"""MCP tool registrations for tags."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.tag import Tag, TagCreate, TagPatch
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register tag tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_tags"))
    @paperless_errors
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

    @mcp.tool(**tool_metadata("get_tag"))
    @paperless_errors
    async def get_tag(tag_id: int) -> Tag:
        """Fetch a tag by ID."""
        return await client.tags.get(tag_id)

    @mcp.tool(**tool_metadata("create_tag"))
    @paperless_errors
    async def create_tag(body: TagCreate) -> Tag:
        """Create a new tag."""
        return await client.tags.create(body)

    @mcp.tool(**tool_metadata("update_tag"))
    @paperless_errors
    async def update_tag(tag_id: int, patch: TagPatch) -> Tag:
        """Patch selected fields on a tag."""
        return await client.tags.update(tag_id, patch)

    @mcp.tool(**tool_metadata("delete_tag"))
    @paperless_errors
    async def delete_tag(tag_id: int) -> None:
        """Delete a tag."""
        await client.tags.delete(tag_id)

    @mcp.tool(**tool_metadata("bulk_edit_tags"))
    @paperless_errors
    async def bulk_edit_tags(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of tags."""
        return await client.tags.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
