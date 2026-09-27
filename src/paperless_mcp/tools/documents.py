"""MCP tool registrations for Paperless documents."""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp_pvl_core import tool_boundary
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
from paperless_mcp.tools._params import (
    BulkIds,
    DocumentId,
    DocumentOrdering,
    Page,
    PageSize,
)


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
    @tool_boundary
    @paperless_errors
    async def list_documents(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        ordering: DocumentOrdering = None,
        tags: list[int] | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        storage_path: int | None = None,
        custom_field: int | None = None,
    ) -> Paginated[Document]:
        """List documents filtered by their metadata; returns one page of metadata.

        Use search_documents to find documents by the words in them. Results
        leave out each document's text, note text and custom field values;
        get_document_content and get_document return them.

        Args:
            tags: Keep documents that carry any of these tag ids.
            correspondent: Keep documents from this correspondent id.
            document_type: Keep documents of this document type id.
            storage_path: Keep documents in this storage path id.
            custom_field: Keep documents that have this custom field.
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
    @tool_boundary
    @paperless_errors
    async def search_documents(
        query: str,
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        more_like: int | None = None,
    ) -> Paginated[Document]:
        """Search the full text and metadata of documents; returns one page, best match first.

        Use list_documents to filter by tag, correspondent or type alone.
        Results leave out each document's text, note text and custom field
        values; get_document_content and get_document return them.

        Args:
            query: Words that must all appear, in any order, in a document's
                text, title, correspondent, type or tags. Also accepts AND and
                OR, field terms such as tag:unpaid or created:[2024 to 2025],
                and notes.note:word for note text. Pass "" with more_like.
            more_like: Document id; return documents similar to it instead.
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
    @tool_boundary
    @paperless_errors
    async def get_document(document_id: DocumentId) -> Document:
        """Get one document's metadata, notes and custom field values, without its text.

        Use get_document_content for the text.
        """
        doc = await client.documents.get(document_id)
        doc.content = None
        _with_web_url(doc)
        return doc

    @mcp.tool(**tool_metadata("get_document_content"))
    @tool_boundary
    @paperless_errors
    async def get_document_content(
        document_id: DocumentId,
        max_chars: Annotated[int, Field(gt=0, le=CONTENT_CHAR_CAP)] = CONTENT_CHAR_CAP,
        offset: Annotated[int, Field(ge=0)] = 0,
    ) -> str:
        """Read a document's text, up to 20,000 characters per call.

        A longer document comes back in sections: each opens with a marker
        naming the range returned, the full length and the offset of the next
        section. Text that fits is returned whole, with no marker.

        Args:
            max_chars: Most characters to return in this call.
            offset: Character position to start from; pass the offset a marker
                names to read the next section.
        """
        text = await client.documents.get_content(document_id)
        return slice_content(text, max_chars=max_chars, offset=offset)

    @mcp.tool(**tool_metadata("get_document_thumbnail"))
    @tool_boundary
    @paperless_errors
    async def get_document_thumbnail(document_id: DocumentId) -> ImageContent:
        """Get a small image of a document's first page."""
        data, content_type = await client.documents.get_thumbnail(document_id)
        return ImageContent(
            type="image",
            data=base64.b64encode(data).decode("ascii"),
            mime_type=content_type or "image/png",
        )

    @mcp.tool(**tool_metadata("get_document_metadata"))
    @tool_boundary
    @paperless_errors
    async def get_document_metadata(document_id: DocumentId) -> DocumentMetadata:
        """Get a document's file details: original and archived file names, sizes, checksums and MIME type."""
        return await client.documents.get_metadata(document_id)

    @mcp.tool(**tool_metadata("get_document_notes"))
    @tool_boundary
    @paperless_errors
    async def get_document_notes(document_id: DocumentId) -> list[DocumentNote]:
        """List the notes on a document, with their full text."""
        return await client.documents.get_notes(document_id)

    @mcp.tool(**tool_metadata("get_document_history"))
    @tool_boundary
    @paperless_errors
    async def get_document_history(
        document_id: DocumentId,
    ) -> list[DocumentHistoryEntry]:
        """List the changes made to a document: who changed which field, and when."""
        return await client.documents.get_history(document_id)

    @mcp.tool(**tool_metadata("get_document_suggestions"))
    @tool_boundary
    @paperless_errors
    async def get_document_suggestions(document_id: DocumentId) -> DocumentSuggestions:
        """Get Paperless's suggested tags, correspondent, document type and dates for a document."""
        return await client.documents.get_suggestions(document_id)

    @mcp.tool(**tool_metadata("update_document"))
    @tool_boundary
    @paperless_errors
    async def update_document(
        document_id: DocumentId,
        patch: DocumentPatch,
    ) -> Document:
        """Change a document's metadata; returns the updated document without its text.

        Use bulk_edit_documents to change many documents at once.

        Args:
            patch: Only the fields to change.
        """
        doc = await client.documents.update(document_id, patch)
        doc.content = None
        _with_web_url(doc)
        return doc

    @mcp.tool(**tool_metadata("delete_document"))
    @tool_boundary
    @paperless_errors
    async def delete_document(document_id: DocumentId) -> None:
        """Move a document to Paperless's trash, where a user can restore it until the trash is emptied."""
        await client.documents.delete(document_id)

    @mcp.tool(**tool_metadata("upload_document"))
    @tool_boundary
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
        """Upload a file for Paperless to consume; returns the consume task's id.

        The document appears once the task finishes; wait_for_task waits for
        it and its result names the new document. For large files, use
        create_upload_link where it is available.

        Args:
            filename: File name, with the extension that tells Paperless its type.
            content_base64: The file's bytes, base64-encoded.
            title: Title; omit to let Paperless derive one.
            correspondent: Correspondent id.
            document_type: Document type id.
            tags: Tag ids to add.
            created: Creation date, YYYY-MM-DD or ISO 8601.
            archive_serial_number: Archive serial number, a whole number.
            custom_fields: Custom field ids to attach, without values.
        """
        try:
            # Whitespace is dropped first so line-wrapped base64 keeps working;
            # validate=True then refuses any other stray character instead of
            # silently skipping it and uploading a corrupted file.
            content = base64.b64decode("".join(content_base64.split()), validate=True)
        except binascii.Error as exc:
            raise ToolError(
                "content_base64 passed to upload_document is not valid base64. "
                "Encode the file's bytes as standard base64 and call "
                "upload_document again.",
                log_level=logging.INFO,
            ) from exc
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
    @tool_boundary
    @paperless_errors
    async def bulk_edit_documents(
        operation: BulkEditOperation,
        ids: BulkIds,
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Apply one operation to many documents at once; returns OK once Paperless accepts it.

        Metadata operations (set_*, add_tag, remove_tag, modify_tags,
        modify_custom_fields, set_permissions) are applied before the reply:
        list_documents and get_document show them at once, search_documents
        only after the bulk_update reindex task in list_tasks. delete, reprocess
        and the PDF operations run as their own background tasks.

        Args:
            operation: What to do to every document in ids.
            parameters: Arguments for the operation: set_correspondent
                {"correspondent": id}, set_document_type {"document_type": id},
                set_storage_path {"storage_path": id}, add_tag and remove_tag
                {"tag": id}, modify_tags {"add_tags": [ids], "remove_tags":
                [ids]}, modify_custom_fields {"add_custom_fields": [ids] or
                {"<id>": value}, "remove_custom_fields": [ids]}, set_permissions
                {"set_permissions": {"view": {"users": [ids], "groups": [ids]},
                "change": {...}}, "owner": id, "merge": bool}, rotate
                {"degrees": 90}, merge {"metadata_document_id": id,
                "delete_originals": bool}, and on a single document: split
                {"pages": "1,2-3"}, delete_pages {"pages": [2, 3]}, edit_pdf
                {"operations": [{"page": 1, "rotate": 90, "doc": 0}]} (pages
                left out are dropped; doc numbers the output file),
                remove_password {"password": text}. delete and reprocess take
                none.
        """
        return await client.documents.bulk_edit(
            document_ids=ids, method=operation, parameters=parameters
        )

    @mcp.tool(**tool_metadata("add_document_note"))
    @tool_boundary
    @paperless_errors
    async def add_document_note(document_id: DocumentId, note: str) -> DocumentNote:
        """Add a note to a document; returns the new note with its id.

        Args:
            note: Text of the note.
        """
        return await client.documents.add_note(document_id, note)

    @mcp.tool(**tool_metadata("delete_document_note"))
    @tool_boundary
    @paperless_errors
    async def delete_document_note(document_id: DocumentId, note_id: int) -> None:
        """Delete one note from a document.

        Args:
            note_id: Id of the note, from get_document_notes.
        """
        await client.documents.delete_note(document_id, note_id)
