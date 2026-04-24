"""MCP tool registrations for document types."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.document_type import (
    DocumentType,
    DocumentTypeCreate,
    DocumentTypePatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register document type tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_document_types", read_only_mode=read_only)
    async def list_document_types(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[DocumentType]:
        """List document types."""
        return await client.document_types.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @register_tool(mcp, "get_document_type", read_only_mode=read_only)
    async def get_document_type(document_type_id: int) -> DocumentType:
        """Fetch a document type by ID."""
        return await client.document_types.get(document_type_id)

    @register_tool(mcp, "create_document_type", read_only_mode=read_only)
    async def create_document_type(body: DocumentTypeCreate) -> DocumentType:
        """Create a new document type."""
        return await client.document_types.create(body)

    @register_tool(mcp, "update_document_type", read_only_mode=read_only)
    async def update_document_type(
        document_type_id: int, patch: DocumentTypePatch
    ) -> DocumentType:
        """Patch selected fields on a document type."""
        return await client.document_types.update(document_type_id, patch)

    @register_tool(mcp, "delete_document_type", read_only_mode=read_only)
    async def delete_document_type(document_type_id: int) -> None:
        """Delete a document type."""
        await client.document_types.delete(document_type_id)

    @register_tool(mcp, "bulk_edit_document_types", read_only_mode=read_only)
    async def bulk_edit_document_types(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of document types."""
        return await client.document_types.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
