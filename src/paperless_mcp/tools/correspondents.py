"""MCP tool registrations for correspondents."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.correspondent import (
    Correspondent,
    CorrespondentCreate,
    CorrespondentPatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register correspondent tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_correspondents"))
    @paperless_errors
    async def list_correspondents(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[Correspondent]:
        """List correspondents.

        Each row's ``last_correspondence`` is the date of the correspondent's
        newest document, or null when it has none; ``ordering`` accepts it.
        """
        return await client.correspondents.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @mcp.tool(**tool_metadata("get_correspondent"))
    @paperless_errors
    async def get_correspondent(correspondent_id: int) -> Correspondent:
        """Fetch a correspondent by ID."""
        return await client.correspondents.get(correspondent_id)

    @mcp.tool(**tool_metadata("create_correspondent"))
    @paperless_errors
    async def create_correspondent(body: CorrespondentCreate) -> Correspondent:
        """Create a new correspondent."""
        return await client.correspondents.create(body)

    @mcp.tool(**tool_metadata("update_correspondent"))
    @paperless_errors
    async def update_correspondent(
        correspondent_id: int, patch: CorrespondentPatch
    ) -> Correspondent:
        """Patch selected fields on a correspondent."""
        return await client.correspondents.update(correspondent_id, patch)

    @mcp.tool(**tool_metadata("delete_correspondent"))
    @paperless_errors
    async def delete_correspondent(correspondent_id: int) -> None:
        """Delete a correspondent."""
        await client.correspondents.delete(correspondent_id)

    @mcp.tool(**tool_metadata("bulk_edit_correspondents"))
    @paperless_errors
    async def bulk_edit_correspondents(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of correspondents."""
        return await client.correspondents.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
