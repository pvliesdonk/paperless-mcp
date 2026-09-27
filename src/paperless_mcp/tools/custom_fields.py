"""MCP tool registrations for custom fields."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.custom_field import (
    CustomField,
    CustomFieldCreate,
    CustomFieldPatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import Ordering, Page, PageSize


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register custom field tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_custom_fields"))
    @tool_boundary
    @paperless_errors
    async def list_custom_fields(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: Ordering = None,
    ) -> Paginated[CustomField]:
        """List custom field definitions; returns one page with their ids, names and types."""
        return await client.custom_fields.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @mcp.tool(**tool_metadata("get_custom_field"))
    @tool_boundary
    @paperless_errors
    async def get_custom_field(field_id: int) -> CustomField:
        """Get one custom field definition by id, with its select options."""
        return await client.custom_fields.get(field_id)

    @mcp.tool(**tool_metadata("create_custom_field"))
    @tool_boundary
    @paperless_errors
    async def create_custom_field(body: CustomFieldCreate) -> CustomField:
        """Define a new custom field; returns it with its id.

        Args:
            body: The field's name, type and, for select or monetary, extra_data.
        """
        return await client.custom_fields.create(body)

    @mcp.tool(**tool_metadata("update_custom_field"))
    @tool_boundary
    @paperless_errors
    async def update_custom_field(
        field_id: int, patch: CustomFieldPatch
    ) -> CustomField:
        """Rename a custom field or change its options; returns the updated field.

        Args:
            patch: Only the fields to change.
        """
        return await client.custom_fields.update(field_id, patch)

    @mcp.tool(**tool_metadata("delete_custom_field"))
    @tool_boundary
    @paperless_errors
    async def delete_custom_field(field_id: int) -> None:
        """Delete a custom field and its value on every document."""
        await client.custom_fields.delete(field_id)
