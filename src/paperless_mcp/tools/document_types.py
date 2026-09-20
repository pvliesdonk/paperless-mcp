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
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register document type tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_document_types"))
    @paperless_errors
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

    @mcp.tool(**tool_metadata("get_document_type"))
    @paperless_errors
    async def get_document_type(document_type_id: int) -> DocumentType:
        """Fetch a document type by ID."""
        return await client.document_types.get(document_type_id)

    @mcp.tool(**tool_metadata("create_document_type"))
    @paperless_errors
    async def create_document_type(body: DocumentTypeCreate) -> DocumentType:
        """Create a new document type."""
        return await client.document_types.create(body)

    @mcp.tool(**tool_metadata("update_document_type"))
    @paperless_errors
    async def update_document_type(
        document_type_id: int, patch: DocumentTypePatch
    ) -> DocumentType:
        """Patch selected fields on a document type."""
        return await client.document_types.update(document_type_id, patch)

    @mcp.tool(**tool_metadata("delete_document_type"))
    @paperless_errors
    async def delete_document_type(document_type_id: int) -> None:
        """Delete a document type."""
        await client.document_types.delete(document_type_id)

    @mcp.tool(**tool_metadata("bulk_edit_document_types"))
    @paperless_errors
    async def bulk_edit_document_types(
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of document types."""
        return await client.document_types.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
