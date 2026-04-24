"""MCP tool registrations for custom fields."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.custom_field import (
    CustomField,
    CustomFieldCreate,
    CustomFieldPatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register custom field tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_custom_fields", read_only_mode=read_only)
    async def list_custom_fields(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
    ) -> Paginated[CustomField]:
        """List custom fields."""
        return await client.custom_fields.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @register_tool(mcp, "get_custom_field", read_only_mode=read_only)
    async def get_custom_field(field_id: int) -> CustomField:
        """Fetch a custom field by ID."""
        return await client.custom_fields.get(field_id)

    @register_tool(mcp, "create_custom_field", read_only_mode=read_only)
    async def create_custom_field(body: CustomFieldCreate) -> CustomField:
        """Create a new custom field.

        ``extra_data`` depends on ``data_type``:

        - ``string``, ``longtext``, ``integer``, ``boolean``, ``float``,
          ``date``, ``url``, ``documentlink`` — unused; omit or pass ``null``.
        - ``monetary`` — optional ``{"default_currency": "USD"}`` (ISO-4217).
        - ``select`` — required
          ``{"select_options": [{"label": "Low"}, {"label": "Medium"}]}``.
          Paperless assigns each option a stable ``id`` on creation.

        Unknown shapes are rejected by Paperless with a 400.
        """
        return await client.custom_fields.create(body)

    @register_tool(mcp, "update_custom_field", read_only_mode=read_only)
    async def update_custom_field(
        field_id: int, patch: CustomFieldPatch
    ) -> CustomField:
        """Patch selected fields on a custom field definition.

        For ``select`` fields, ``extra_data.select_options`` replaces the
        current list wholesale.  To preserve existing values, include each
        existing option with its server-assigned ``id``:
        ``{"select_options": [{"id": "abc", "label": "Low"}, ...]}``.
        Omitting an option's ``id`` creates a new option; dropping an option
        from the list deletes it and any document values referencing it.
        See ``create_custom_field`` for the full ``extra_data`` shape table.
        """
        return await client.custom_fields.update(field_id, patch)

    @register_tool(mcp, "delete_custom_field", read_only_mode=read_only)
    async def delete_custom_field(field_id: int) -> None:
        """Delete a custom field."""
        await client.custom_fields.delete(field_id)

    @register_tool(mcp, "bulk_edit_custom_fields", read_only_mode=read_only)
    async def bulk_edit_custom_fields(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of custom fields."""
        return await client.custom_fields.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
