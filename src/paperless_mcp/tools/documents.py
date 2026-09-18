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

#: Default ceiling on inline OCR text returned by ``get_document_content``.
#:
#: Chosen as a per-call context budget rather than to fit any particular
#: document: ~7k tokens of real OCR text, which one tool result can spend
#: without crowding out the rest of a conversation.  Deliberately defensive —
#: most documents in a text-heavy archive arrive in sections rather than whole,
#: which ``offset`` makes cheap.  See ``docs/design/inline-content-size.md``
#: for the measured distribution the number is drawn from.
CONTENT_CHAR_CAP = 50_000


def _content_marker(*, offset: int, end: int, total: int) -> str:
    """Build the header line that precedes a partial document slice.

    Args:
        offset: First character index of the returned slice.
        end: One past the last character index of the returned slice.
        total: Full length of the document's text.

    Returns:
        A one-line marker ending in a blank line, naming the range returned
        and — when text remains — the exact ``offset`` to pass next.
    """
    if offset >= total:
        return f"[offset {offset:,} is past the end of this document ({total:,} chars)]\n\n"
    if end >= total:
        return f"[chars {offset:,}-{total:,} of {total:,} - final section]\n\n"
    return (
        f"[chars {offset:,}-{end:,} of {total:,} - truncated; call "
        f"get_document_content again with offset={end} to continue]\n\n"
    )


def _slice_content(text: str, *, max_chars: int | None, offset: int) -> str:
    """Return *text* from *offset*, capped at *max_chars*.

    Text returned whole — the common case of a short document read from the
    start — comes back byte-identical with no marker, so callers that never
    hit the cap see exactly what they saw before the cap existed.

    Args:
        text: The document's full OCR text.
        max_chars: Maximum characters to return, or ``None`` for no cap.
        offset: Character position to start from.

    Returns:
        The requested slice, prefixed by a marker when it is not the whole text.
    """
    total = len(text)
    end = total if max_chars is None else min(total, offset + max_chars)
    if offset == 0 and end >= total:
        return text
    return _content_marker(offset=offset, end=end, total=total) + text[offset:end]


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

    @register_tool(mcp, "list_documents")
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

        ``notes[].note`` and ``custom_fields[].value`` are **always** stripped
        from listings regardless of ``include_content`` — the metadata refs
        (note ids, timestamps, custom-field ids) are retained so callers can
        detect presence, but to read the actual text use ``get_document``
        (with ``include_content=True`` if needed) or ``get_document_notes``.
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

    @register_tool(mcp, "search_documents")
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

        ``notes[].note`` and ``custom_fields[].value`` are **always** stripped
        from search hits regardless of ``include_content`` — fetch them via
        ``get_document`` or ``get_document_notes`` when needed.
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

    @register_tool(mcp, "get_document")
    async def get_document(
        document_id: int,
        include_content: bool = False,
    ) -> Document:
        """Fetch one document by ID.

        By default, the OCR ``content`` is stripped to keep responses small.
        Pass ``include_content=True`` for the full text however long it is, or
        call ``get_document_content`` for the text alone, which caps its length
        by default and can page through a long document.
        """
        doc = await client.documents.get(document_id)
        if not include_content:
            doc.content = None
        _with_web_url(doc)
        return doc

    @register_tool(mcp, "get_document_content")
    async def get_document_content(
        document_id: int,
        max_chars: Annotated[int | None, Field(gt=0)] = CONTENT_CHAR_CAP,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> str:
        """Return the OCR'd text content of a document.

        Documents such as books and technical standards can run to millions of
        characters, so the text is capped by default.  A capped result opens
        with a marker naming the character range returned, the document's full
        length, and the ``offset`` to pass to read the next section; text that
        fits under the cap is returned whole with no marker.

        Args:
            document_id: ID of the document to read.
            max_chars: Maximum number of characters to return.  Pass ``None``
                for the entire text however long it is.
            offset: Character position to start reading from.  Pass the value
                named in a truncation marker to continue from where it stopped.

        Returns:
            The document's text, prefixed with a marker when the returned
            section is not the whole document.
        """
        text = await client.documents.get_content(document_id)
        return _slice_content(text, max_chars=max_chars, offset=offset)

    @register_tool(mcp, "get_document_thumbnail")
    async def get_document_thumbnail(document_id: int) -> ImageContent:
        """Return the document's thumbnail as inline image content."""
        data, content_type = await client.documents.get_thumbnail(document_id)
        return ImageContent(
            type="image",
            data=base64.b64encode(data).decode("ascii"),
            mime_type=content_type or "image/png",
        )

    @register_tool(mcp, "get_document_metadata")
    async def get_document_metadata(document_id: int) -> DocumentMetadata:
        """Return technical metadata for a document (checksums, filenames, etc.)."""
        return await client.documents.get_metadata(document_id)

    @register_tool(mcp, "get_document_notes")
    async def get_document_notes(document_id: int) -> list[DocumentNote]:
        """Return notes attached to a document."""
        return await client.documents.get_notes(document_id)

    @register_tool(mcp, "get_document_history")
    async def get_document_history(document_id: int) -> list[DocumentHistoryEntry]:
        """Return the audit history for a document."""
        return await client.documents.get_history(document_id)

    @register_tool(mcp, "get_document_suggestions")
    async def get_document_suggestions(document_id: int) -> DocumentSuggestions:
        """Return Paperless's classifier suggestions for a document."""
        return await client.documents.get_suggestions(document_id)

    @register_tool(mcp, "update_document")
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

    @register_tool(mcp, "delete_document")
    async def delete_document(document_id: int) -> None:
        """Delete a document."""
        await client.documents.delete(document_id)

    @register_tool(mcp, "upload_document")
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

    @register_tool(mcp, "bulk_edit_documents")
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

    @register_tool(mcp, "add_document_note")
    async def add_document_note(document_id: int, note: str) -> DocumentNote:
        """Append a note to a document."""
        return await client.documents.add_note(document_id, note)

    @register_tool(mcp, "delete_document_note")
    async def delete_document_note(document_id: int, note_id: int) -> None:
        """Remove a note from a document."""
        await client.documents.delete_note(document_id, note_id)
