"""MCP tool registrations for storage paths (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.storage_path import StoragePath
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register storage path tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_storage_paths", read_only_mode=read_only)
    async def list_storage_paths(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
    ) -> Paginated[StoragePath]:
        """List storage paths."""
        return await client.storage_paths.list(
            page=page, page_size=page_size, ordering=ordering
        )

    @register_tool(mcp, "get_storage_path", read_only_mode=read_only)
    async def get_storage_path(storage_path_id: int) -> StoragePath:
        """Fetch a storage path by ID."""
        return await client.storage_paths.get(storage_path_id)
