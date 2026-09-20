"""MCP tool registrations for Paperless documents."""

from __future__ import annotations

import base64
from typing import Annotated

from fastmcp import FastMCP
from mcp.types import ImageContent
from pydantic import Field

from paperless_mcp._content import CONTENT_CHAR_CAP, slice_content
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
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register document tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    def _with_web_url(doc: Document) -> None:
        """Populate *doc*'s ``web_url`` when a public URL is configured."""
        if ctx.public_url:
            doc.web_url = f"{ctx.public_url}/documents/{doc.id}/"

    @mcp.tool(**tool_metadata("list_documents"))
    @paperless_errors
    async def list_documents(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        ordering: str | None = None,
        tags: list[int] | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        storage_path: int | None = None,
        custom_field: int | None = None,
    ) -> Paginated[Document]:
        """List documents with optional filters.  Returns one page.

        Per-document OCR ``content`` is stripped to keep results small. Use
        ``get_document_content`` for a bounded preview of one result.

        ``notes[].note`` and ``custom_fields[].value`` are **always** stripped
        from listings. The metadata refs
        (note ids, timestamps, custom-field ids) are retained so callers can
        detect presence; use ``get_document`` or ``get_document_notes`` to read
        those values.
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
            include_content=False,
        )
        for doc in result.results:
            _with_web_url(doc)
        return result

    @mcp.tool(**tool_metadata("search_documents"))
    @paperless_errors
    async def search_documents(
        query: str,
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        more_like: int | None = None,
    ) -> Paginated[Document]:
        """Full-text search documents.

        Per-hit OCR ``content`` is stripped. Use ``get_document_content`` for a
        bounded preview of one hit. Use *more_like* for similarity search.

        ``notes[].note`` and ``custom_fields[].value`` are **always** stripped
        from search hits; fetch them via ``get_document`` or
        ``get_document_notes`` when needed.
        """
        result = await client.documents.search(
            query,
            page=page,
            page_size=page_size,
            more_like=more_like,
            include_content=False,
        )
        for doc in result.results:
            _with_web_url(doc)
        return result

    @mcp.tool(**tool_metadata("get_document"))
    @paperless_errors
    async def get_document(document_id: int) -> Document:
        """Fetch one document by ID.

        OCR ``content`` is stripped to keep responses small. Call
        ``get_document_content`` for a bounded preview, or use
        ``create_download_link`` with the content variant when available.
        """
        doc = await client.documents.get(document_id)
        doc.content = None
        _with_web_url(doc)
        return doc

    @mcp.tool(**tool_metadata("get_document_content"))
    @paperless_errors
    async def get_document_content(
        document_id: int,
        max_chars: Annotated[int, Field(gt=0, le=CONTENT_CHAR_CAP)] = CONTENT_CHAR_CAP,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> str:
        """Return the OCR'd text content of a document.

        Documents such as books and technical standards can run to millions of
        characters, so each call is capped at 20,000. A partial result opens
        with a marker naming the character range returned, the document's full
        length, and the ``offset`` to pass to read the next section; text that
        fits under the cap is returned whole with no marker.

        Args:
            document_id: ID of the document to read.
            max_chars: Maximum number of characters to return, up to 20,000.
            offset: Character position to start reading from.  Pass the value
                named in a truncation marker to continue from where it stopped.

        Returns:
            The document's text, prefixed with a marker when the returned
            section is not the whole document.
        """
        text = await client.documents.get_content(document_id)
        return slice_content(text, max_chars=max_chars, offset=offset)

    @mcp.tool(**tool_metadata("get_document_thumbnail"))
    @paperless_errors
    async def get_document_thumbnail(document_id: int) -> ImageContent:
        """Return the document's thumbnail as inline image content."""
        data, content_type = await client.documents.get_thumbnail(document_id)
        return ImageContent(
            type="image",
            data=base64.b64encode(data).decode("ascii"),
            mime_type=content_type or "image/png",
        )

    @mcp.tool(**tool_metadata("get_document_metadata"))
    @paperless_errors
    async def get_document_metadata(document_id: int) -> DocumentMetadata:
        """Return technical metadata for a document (checksums, filenames, etc.)."""
        return await client.documents.get_metadata(document_id)

    @mcp.tool(**tool_metadata("get_document_notes"))
    @paperless_errors
    async def get_document_notes(document_id: int) -> list[DocumentNote]:
        """Return notes attached to a document."""
        return await client.documents.get_notes(document_id)

    @mcp.tool(**tool_metadata("get_document_history"))
    @paperless_errors
    async def get_document_history(document_id: int) -> list[DocumentHistoryEntry]:
        """Return the audit history for a document."""
        return await client.documents.get_history(document_id)

    @mcp.tool(**tool_metadata("get_document_suggestions"))
    @paperless_errors
    async def get_document_suggestions(document_id: int) -> DocumentSuggestions:
        """Return Paperless's classifier suggestions for a document."""
        return await client.documents.get_suggestions(document_id)

    @mcp.tool(**tool_metadata("update_document"))
    @paperless_errors
    async def update_document(
        document_id: int,
        patch: DocumentPatch,
    ) -> Document:
        """Patch selected fields on a document.

        The response strips OCR ``content``. Use ``get_document_content`` or a
        transfer link when the updated text is needed.
        """
        doc = await client.documents.update(document_id, patch)
        doc.content = None
        _with_web_url(doc)
        return doc

    @mcp.tool(**tool_metadata("delete_document"))
    @paperless_errors
    async def delete_document(document_id: int) -> None:
        """Delete a document."""
        await client.documents.delete(document_id)

    @mcp.tool(**tool_metadata("upload_document"))
    @paperless_errors
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

    @mcp.tool(**tool_metadata("bulk_edit_documents"))
    @paperless_errors
    async def bulk_edit_documents(
        operation: BulkEditOperation,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply a bulk operation to a set of documents.

        Paperless writes the change before answering ``OK``, then queues the
        search-index rebuild as a background task.  A following
        ``search_documents`` call can therefore miss the edited documents for
        seconds to minutes, while ``list_documents`` and ``get_document``
        reflect the change at once.  Metadata operations queue a
        ``bulk_update`` task: find it with
        ``list_tasks(task_type="bulk_update")`` and ``wait_for_task`` on its
        ``task_id`` to wait for full-text search to catch up.
        """
        return await client.documents.bulk_edit(
            document_ids=ids, method=operation, parameters=parameters
        )

    @mcp.tool(**tool_metadata("add_document_note"))
    @paperless_errors
    async def add_document_note(document_id: int, note: str) -> DocumentNote:
        """Append a note to a document."""
        return await client.documents.add_note(document_id, note)

    @mcp.tool(**tool_metadata("delete_document_note"))
    @paperless_errors
    async def delete_document_note(document_id: int, note_id: int) -> None:
        """Remove a note from a document."""
        await client.documents.delete_note(document_id, note_id)
