"""MCP tool registrations for storage paths (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.storage_path import StoragePath
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register storage path tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_storage_paths"))
    @paperless_errors
    async def list_storage_paths(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
    ) -> Paginated[StoragePath]:
        """List storage paths."""
        return await client.storage_paths.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @mcp.tool(**tool_metadata("get_storage_path"))
    @paperless_errors
    async def get_storage_path(storage_path_id: int) -> StoragePath:
        """Fetch a storage path by ID."""
        return await client.storage_paths.get(storage_path_id)
