"""MCP tool registrations for document types."""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP
from fastmcp_pvl_core import tool_boundary

from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.document_type import (
    DocumentType,
    DocumentTypeCreate,
    DocumentTypePatch,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import check_object_bulk_parameters, paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import (
    BulkIds,
    NameContains,
    ObjectBulkParameters,
    Ordering,
    Page,
    PageSize,
)


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register document type tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_document_types"))
    @tool_boundary
    @paperless_errors
    async def list_document_types(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: Ordering = None,
        name__icontains: NameContains = None,
    ) -> Paginated[DocumentType]:
        """List document types; returns one page with their ids and names."""
        return await client.document_types.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            name__icontains=name__icontains,
        )

    @mcp.tool(**tool_metadata("get_document_type"))
    @tool_boundary
    @paperless_errors
    async def get_document_type(document_type_id: int) -> DocumentType:
        """Get one document type by id."""
        return await client.document_types.get(document_type_id)

    @mcp.tool(**tool_metadata("create_document_type"))
    @tool_boundary
    @paperless_errors
    async def create_document_type(body: DocumentTypeCreate) -> DocumentType:
        """Create a document type; returns it with its id."""
        return await client.document_types.create(body)

    @mcp.tool(**tool_metadata("update_document_type"))
    @tool_boundary
    @paperless_errors
    async def update_document_type(
        document_type_id: int, patch: DocumentTypePatch
    ) -> DocumentType:
        """Change a document type's name or matching rule; returns the updated document type.

        Args:
            patch: Only the fields to change.
        """
        return await client.document_types.update(document_type_id, patch)

    @mcp.tool(**tool_metadata("delete_document_type"))
    @tool_boundary
    @paperless_errors
    async def delete_document_type(document_type_id: int) -> None:
        """Delete a document type and clear it from every document of that type."""
        await client.document_types.delete(document_type_id)

    @mcp.tool(**tool_metadata("bulk_edit_document_types"))
    @tool_boundary
    @paperless_errors
    async def bulk_edit_document_types(
        operation: Literal["set_permissions", "delete"],
        ids: BulkIds,
        parameters: ObjectBulkParameters = None,
    ) -> BulkEditResult:
        """Set the owner and permissions of many document types, or delete them; returns OK when applied.

        Args:
            operation: set_permissions or delete.
        """
        check_object_bulk_parameters("bulk_edit_document_types", operation, parameters)
        return await client.document_types.bulk_edit(
            operation=operation, ids=ids, parameters=parameters
        )
