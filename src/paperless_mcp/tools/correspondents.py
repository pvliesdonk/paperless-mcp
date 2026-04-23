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
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register correspondent tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_correspondents", read_only_mode=read_only)
    async def list_correspondents(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = 100,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[Correspondent]:
        """List correspondents."""
        return await client.correspondents.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @register_tool(mcp, "get_correspondent", read_only_mode=read_only)
    async def get_correspondent(correspondent_id: int) -> Correspondent:
        """Fetch a correspondent by ID."""
        return await client.correspondents.get(correspondent_id)

    @register_tool(mcp, "create_correspondent", read_only_mode=read_only)
    async def create_correspondent(body: CorrespondentCreate) -> Correspondent:
        """Create a new correspondent."""
        return await client.correspondents.create(body)

    @register_tool(mcp, "update_correspondent", read_only_mode=read_only)
    async def update_correspondent(
        correspondent_id: int, patch: CorrespondentPatch
    ) -> Correspondent:
        """Patch selected fields on a correspondent."""
        return await client.correspondents.update(correspondent_id, patch)

    @register_tool(mcp, "delete_correspondent", read_only_mode=read_only)
    async def delete_correspondent(correspondent_id: int) -> None:
        """Delete a correspondent."""
        await client.correspondents.delete(correspondent_id)

    @register_tool(mcp, "bulk_edit_correspondents", read_only_mode=read_only)
    async def bulk_edit_correspondents(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of correspondents."""
        return await client.correspondents.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
