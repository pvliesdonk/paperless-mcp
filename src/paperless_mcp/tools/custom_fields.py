"""MCP tool registrations for custom fields."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.custom_field import (
    CustomField,
    CustomFieldCreate,
    CustomFieldPatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register custom field tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_custom_fields"))
    @paperless_errors
    async def list_custom_fields(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
    ) -> Paginated[CustomField]:
        """List custom fields."""
        return await client.custom_fields.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @mcp.tool(**tool_metadata("get_custom_field"))
    @paperless_errors
    async def get_custom_field(field_id: int) -> CustomField:
        """Fetch a custom field by ID."""
        return await client.custom_fields.get(field_id)

    @mcp.tool(**tool_metadata("create_custom_field"))
    @paperless_errors
    async def create_custom_field(body: CustomFieldCreate) -> CustomField:
        """Create a new custom field.

        ``extra_data`` depends on ``data_type``:

        - ``string``, ``longtext``, ``integer``, ``boolean``, ``float``,
          ``date``, ``url``, ``documentlink`` — unused; omit or pass ``null``.
        - ``monetary`` — optional ``{"default_currency": "USD"}`` (ISO-4217).
        - ``select`` — ``extra_data`` **required**:
          ``{"select_options": [{"label": "Low"}, {"label": "Medium"}]}``.
          Paperless assigns each option a stable ``id`` on creation.

        Unknown shapes are rejected by Paperless with a 400.
        """
        return await client.custom_fields.create(body)

    @mcp.tool(**tool_metadata("update_custom_field"))
    @paperless_errors
    async def update_custom_field(
        field_id: int, patch: CustomFieldPatch
    ) -> CustomField:
        """Patch selected fields on a custom field definition.

        ``extra_data`` shape depends on ``data_type``:

        - ``monetary`` — optional ``{"default_currency": "USD"}`` (ISO-4217).
        - ``select`` — ``extra_data.select_options`` replaces the current list
          wholesale.  To preserve existing values, include each existing option
          with its server-assigned ``id``:
          ``{"select_options": [{"id": "abc", "label": "Low"}, ...]}``.
          Omitting an option's ``id`` creates a new option; dropping an option
          from the list deletes it and any document values referencing it.
          A patch without ``extra_data``, such as a rename, keeps the current
          options: the server reads them and sends them back with their ids.

        See ``create_custom_field`` for the full ``extra_data`` shape table.
        """
        return await client.custom_fields.update(field_id, patch)

    @mcp.tool(**tool_metadata("delete_custom_field"))
    @paperless_errors
    async def delete_custom_field(field_id: int) -> None:
        """Delete a custom field."""
        await client.custom_fields.delete(field_id)
