"""MCP tool registrations for tags."""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.tag import Tag, TagCreate, TagPatch
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import check_object_bulk_parameters, paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import (
    BulkIds,
    NameContains,
    ObjectBulkParameters,
    Ordering,
    Page,
    PageSize,
)


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register tag tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_tags"))
    @tool_boundary
    @paperless_errors
    async def list_tags(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: Ordering = None,
        name__icontains: NameContains = None,
    ) -> Paginated[Tag]:
        """List tags; returns one page with their ids and names."""
        return await client.tags.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @mcp.tool(**tool_metadata("get_tag"))
    @tool_boundary
    @paperless_errors
    async def get_tag(tag_id: int) -> Tag:
        """Get one tag by id."""
        return await client.tags.get(tag_id)

    @mcp.tool(**tool_metadata("create_tag"))
    @tool_boundary
    @paperless_errors
    async def create_tag(body: TagCreate) -> Tag:
        """Create a tag; returns it with its id."""
        return await client.tags.create(body)

    @mcp.tool(**tool_metadata("update_tag"))
    @tool_boundary
    @paperless_errors
    async def update_tag(tag_id: int, patch: TagPatch) -> Tag:
        """Change a tag's name, colour, inbox flag or matching rule; returns the tag.

        Args:
            patch: Only the fields to change.
        """
        return await client.tags.update(tag_id, patch)

    @mcp.tool(**tool_metadata("delete_tag"))
    @tool_boundary
    @paperless_errors
    async def delete_tag(tag_id: int) -> None:
        """Delete a tag and remove it from every document that carries it."""
        await client.tags.delete(tag_id)

    @mcp.tool(**tool_metadata("bulk_edit_tags"))
    @tool_boundary
    @paperless_errors
    async def bulk_edit_tags(
        operation: Literal["set_permissions", "delete"],
        ids: BulkIds,
        parameters: ObjectBulkParameters = None,
    ) -> BulkEditResult:
        """Set the owner and permissions of many tags, or delete them; returns OK when applied.

        Args:
            operation: set_permissions or delete.
        """
        check_object_bulk_parameters("bulk_edit_tags", operation, parameters)
        return await client.tags.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
