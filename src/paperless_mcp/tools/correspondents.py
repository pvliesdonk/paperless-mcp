"""MCP tool registrations for correspondents."""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.correspondent import (
    Correspondent,
    CorrespondentCreate,
    CorrespondentPatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import check_object_bulk_parameters, paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import (
    BulkIds,
    CorrespondentOrdering,
    NameContains,
    ObjectBulkParameters,
    Page,
    PageSize,
)


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register correspondent tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_correspondents"))
    @tool_boundary
    @paperless_errors
    async def list_correspondents(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: CorrespondentOrdering = None,
        name__icontains: NameContains = None,
    ) -> Paginated[Correspondent]:
        """List correspondents; returns one page with their ids and names.

        Each carries last_correspondence, the date of its newest document.
        """
        return await client.correspondents.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @mcp.tool(**tool_metadata("get_correspondent"))
    @tool_boundary
    @paperless_errors
    async def get_correspondent(correspondent_id: int) -> Correspondent:
        """Get one correspondent by id."""
        return await client.correspondents.get(correspondent_id)

    @mcp.tool(**tool_metadata("create_correspondent"))
    @tool_boundary
    @paperless_errors
    async def create_correspondent(body: CorrespondentCreate) -> Correspondent:
        """Create a correspondent; returns it with its id."""
        return await client.correspondents.create(body)

    @mcp.tool(**tool_metadata("update_correspondent"))
    @tool_boundary
    @paperless_errors
    async def update_correspondent(
        correspondent_id: int, patch: CorrespondentPatch
    ) -> Correspondent:
        """Change a correspondent's name or matching rule; returns the updated correspondent.

        Args:
            patch: Only the fields to change.
        """
        return await client.correspondents.update(correspondent_id, patch)

    @mcp.tool(**tool_metadata("delete_correspondent"))
    @tool_boundary
    @paperless_errors
    async def delete_correspondent(correspondent_id: int) -> None:
        """Delete a correspondent and clear it from every document that names it."""
        await client.correspondents.delete(correspondent_id)

    @mcp.tool(**tool_metadata("bulk_edit_correspondents"))
    @tool_boundary
    @paperless_errors
    async def bulk_edit_correspondents(
        operation: Literal["set_permissions", "delete"],
        ids: BulkIds,
        parameters: ObjectBulkParameters = None,
    ) -> BulkEditResult:
        """Set the owner and permissions of many correspondents, or delete them; returns OK when applied.

        Args:
            operation: set_permissions or delete.
        """
        check_object_bulk_parameters("bulk_edit_correspondents", operation, parameters)
        return await client.correspondents.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
