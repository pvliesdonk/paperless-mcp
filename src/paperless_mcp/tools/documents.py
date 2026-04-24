"""MCP tool registrations for Paperless documents."""

from __future__ import annotations

import base64
from typing import Annotated

from fastmcp import FastMCP
from mcp.types import ImageContent
from pydantic import Field

from paperless_mcp.models.common import (
    BulkEditOperation,
    BulkEditResult,
    Paginated,
    UploadTaskAcknowledgement,
)
from paperless_mcp.models.document import (
    Document,
    DocumentHistoryEntry,
    DocumentMetadata,
    DocumentNote,
    DocumentPatch,
    DocumentSuggestions,
)
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register document tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    def _with_web_url(doc: Document) -> None:
        """Populate *doc*'s ``web_url`` when a public URL is configured."""
        if ctx.public_url:
            doc.web_url = f"{ctx.public_url}/documents/{doc.id}/"

    @register_tool(mcp, "list_documents", read_only_mode=read_only)
    async def list_documents(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
        tags: list[int] | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        storage_path: int | None = None,
        custom_field: int | None = None,
        include_content: bool = False,
    ) -> Paginated[Document]:
        """List documents with optional filters.  Returns one page.

        By default, per-document OCR ``content`` is stripped to keep results
        small.  Pass ``include_content=True`` for the full text on each hit.
        """
        result = await client.documents.list(
            page=page,
            page_size=page_size,
            ordering=ordering,
            tags=tags,
            correspondent=correspondent,
            document_type=document_type,
            storage_path=storage_path,
            custom_field=custom_field,
            include_content=include_content,
        )
        for doc in result.results:
            _with_web_url(doc)
        return result

    @register_tool(mcp, "search_documents", read_only_mode=read_only)
    async def search_documents(
        query: str,
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        more_like: int | None = None,
        include_content: bool = False,
    ) -> Paginated[Document]:
        """Full-text search documents.

        By default per-hit OCR ``content`` is stripped; pass
        ``include_content=True`` to get full OCR text per hit.
        Use *more_like* for similarity search.
        """
        result = await client.documents.search(
            query,
            page=page,
            page_size=page_size,
            more_like=more_like,
            include_content=include_content,
        )
        for doc in result.results:
            _with_web_url(doc)
        return result

    @register_tool(mcp, "get_document", read_only_mode=read_only)
    async def get_document(
        document_id: int,
        include_content: bool = False,
    ) -> Document:
        """Fetch one document by ID.

        By default, the OCR ``content`` is stripped to keep responses small.
        Pass ``include_content=True`` for the full text, or call
        ``get_document_content`` to retrieve just the text.
        """
        doc = await client.documents.get(document_id)
        if not include_content:
            doc.content = None
        _with_web_url(doc)
        return doc

    @register_tool(mcp, "get_document_content", read_only_mode=read_only)
    async def get_document_content(document_id: int) -> str:
        """Return the OCR'd text content of a document."""
        return await client.documents.get_content(document_id)

    @register_tool(mcp, "get_document_thumbnail", read_only_mode=read_only)
    async def get_document_thumbnail(document_id: int) -> ImageContent:
        """Return the document's thumbnail as inline image content."""
        data, content_type = await client.documents.get_thumbnail(document_id)
        return ImageContent(
            type="image",
            data=base64.b64encode(data).decode("ascii"),
            mimeType=content_type or "image/png",
        )

    @register_tool(mcp, "get_document_metadata", read_only_mode=read_only)
    async def get_document_metadata(document_id: int) -> DocumentMetadata:
        """Return technical metadata for a document (checksums, filenames, etc.)."""
        return await client.documents.get_metadata(document_id)

    @register_tool(mcp, "get_document_notes", read_only_mode=read_only)
    async def get_document_notes(document_id: int) -> list[DocumentNote]:
        """Return notes attached to a document."""
        return await client.documents.get_notes(document_id)

    @register_tool(mcp, "get_document_history", read_only_mode=read_only)
    async def get_document_history(document_id: int) -> list[DocumentHistoryEntry]:
        """Return the audit history for a document."""
        return await client.documents.get_history(document_id)

    @register_tool(mcp, "get_document_suggestions", read_only_mode=read_only)
    async def get_document_suggestions(document_id: int) -> DocumentSuggestions:
        """Return Paperless's classifier suggestions for a document."""
        return await client.documents.get_suggestions(document_id)

    @register_tool(mcp, "update_document", read_only_mode=read_only)
    async def update_document(
        document_id: int,
        patch: DocumentPatch,
        include_content: bool = False,
    ) -> Document:
        """Patch selected fields on a document.

        The response strips OCR ``content`` by default; pass
        ``include_content=True`` to get the full text back.
        """
        doc = await client.documents.update(document_id, patch)
        if not include_content:
            doc.content = None
        _with_web_url(doc)
        return doc

    @register_tool(mcp, "delete_document", read_only_mode=read_only)
    async def delete_document(document_id: int) -> None:
        """Delete a document."""
        await client.documents.delete(document_id)

    @register_tool(mcp, "upload_document", read_only_mode=read_only)
    async def upload_document(
        filename: str,
        content_base64: str,
        title: str | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        tags: list[int] | None = None,
        created: str | None = None,
        archive_serial_number: str | None = None,
        custom_fields: list[int] | None = None,
    ) -> UploadTaskAcknowledgement:
        """Upload a document.  Returns the task UUID for polling via `get_task`."""
        content = base64.b64decode(content_base64)
        return await client.documents.upload(
            filename=filename,
            content=content,
            title=title,
            correspondent=correspondent,
            document_type=document_type,
            tags=tags,
            created=created,
            archive_serial_number=archive_serial_number,
            custom_fields=custom_fields,
        )

    @register_tool(mcp, "bulk_edit_documents", read_only_mode=read_only)
    async def bulk_edit_documents(
        operation: BulkEditOperation,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of documents."""
        return await client.documents.bulk_edit(
            document_ids=ids, method=operation, parameters=parameters
        )

    @register_tool(mcp, "add_document_note", read_only_mode=read_only)
    async def add_document_note(document_id: int, note: str) -> DocumentNote:
        """Append a note to a document."""
        return await client.documents.add_note(document_id, note)

    @register_tool(mcp, "delete_document_note", read_only_mode=read_only)
    async def delete_document_note(document_id: int, note_id: int) -> None:
        """Remove a note from a document."""
        await client.documents.delete_note(document_id, note_id)
