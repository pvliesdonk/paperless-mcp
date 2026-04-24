"""Documents resource client for Paperless-NGX."""

from __future__ import annotations

import builtins
from collections.abc import Sequence

from paperless_mcp.client._http import PaperlessHTTP
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


def _strip_listing_heavy_fields(doc: Document, *, include_content: bool) -> None:
    """Drop per-document heavy fields from list/search responses (see #30).

    Always strips ``notes[].note`` and ``custom_fields[].value`` — metadata refs
    (ids, timestamps, field refs) stay intact so callers can still detect
    presence and dereference via single-document endpoints.  OCR ``content``
    is only stripped when ``include_content`` is ``False``.
    """
    if not include_content:
        doc.content = None
    for note in doc.notes:
        note.note = None
    for cf in doc.custom_fields:
        cf.value = None


class DocumentsClient:
    """Async operations against ``/api/documents/``."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        ordering: str | None = None,
        tags: Sequence[int] | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        storage_path: int | None = None,
        custom_field: int | None = None,
        include_content: bool = False,
    ) -> Paginated[Document]:
        """List documents with optional server-side filtering.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field name to order by (prefix with ``-`` for descending).
            tags: Filter to documents containing all of these tag IDs.
            correspondent: Filter by correspondent ID.
            document_type: Filter by document type ID.
            storage_path: Filter by storage path ID.
            custom_field: Filter by custom field ID.
            include_content: When ``False`` (default), strips the OCR
                ``content`` field from every result to keep responses small.
                Set to ``True`` to retain the full text.  ``notes[].note``
                and ``custom_fields[].value`` are always stripped on list
                responses regardless of this flag (see #30); use
                ``get_document_notes`` and ``get_document`` to fetch them.

        Returns:
            Paginated list of matching :class:`Document` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        if tags is not None:
            params["tags__id__in"] = ",".join(str(t) for t in tags)
        if correspondent is not None:
            params["correspondent__id"] = correspondent
        if document_type is not None:
            params["document_type__id"] = document_type
        if storage_path is not None:
            params["storage_path__id"] = storage_path
        if custom_field is not None:
            params["custom_fields__id"] = custom_field
        body = await self._http.get_json("/api/documents/", params=params)
        result = Paginated[Document].model_validate(body)
        for doc in result.results:
            _strip_listing_heavy_fields(doc, include_content=include_content)
        return result

    async def search(
        self,
        query: str,
        *,
        page: int = 1,
        page_size: int = 25,
        more_like: int | None = None,
        include_content: bool = False,
    ) -> Paginated[Document]:
        """Full-text search for documents.

        Args:
            query: Search query string.
            page: Page number (1-based).
            page_size: Number of results per page.
            more_like: Return documents similar to this document ID.
            include_content: When ``False`` (default), strips the OCR
                ``content`` field from every hit to keep responses small.
                Set to ``True`` to retain the full text.  ``notes[].note``
                and ``custom_fields[].value`` are always stripped on search
                responses regardless of this flag (see #30).

        Returns:
            Paginated list of matching :class:`Document` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if more_like is not None:
            params["more_like_id"] = more_like
        if query:
            params["query"] = query
        body = await self._http.get_json("/api/documents/", params=params)
        result = Paginated[Document].model_validate(body)
        for doc in result.results:
            _strip_listing_heavy_fields(doc, include_content=include_content)
        return result

    async def get(self, document_id: int) -> Document:
        """Fetch a single document by ID.

        Args:
            document_id: ID of the document to retrieve.

        Returns:
            The matching :class:`Document`.
        """
        body = await self._http.get_json(f"/api/documents/{document_id}/")
        return Document.model_validate(body)

    async def get_content(self, document_id: int) -> str:
        """Return the plain-text content of a document.

        Args:
            document_id: ID of the document.

        Returns:
            Extracted text content, or an empty string if none.
        """
        doc = await self.get(document_id)
        return doc.content or ""

    async def get_thumbnail(self, document_id: int) -> tuple[bytes, str]:
        """Download the thumbnail image for a document.

        Args:
            document_id: ID of the document.

        Returns:
            Tuple of ``(image_bytes, content_type)``.
        """
        return await self._http.stream_bytes(f"/api/documents/{document_id}/thumb/")

    async def get_preview(self, document_id: int) -> tuple[bytes, str]:
        """Download the preview PDF for a document.

        Args:
            document_id: ID of the document.

        Returns:
            Tuple of ``(pdf_bytes, content_type)``.
        """
        return await self._http.stream_bytes(f"/api/documents/{document_id}/preview/")

    async def download(
        self, document_id: int, *, original: bool = False
    ) -> tuple[bytes, str]:
        """Download the document file.

        Args:
            document_id: ID of the document.
            original: If ``True``, download the original (unarchived) file.

        Returns:
            Tuple of ``(file_bytes, content_type)``.
        """
        params = {"original": "true"} if original else None
        return await self._http.stream_bytes(
            f"/api/documents/{document_id}/download/", params=params
        )

    async def get_metadata(self, document_id: int) -> DocumentMetadata:
        """Fetch metadata for a document.

        Args:
            document_id: ID of the document.

        Returns:
            :class:`DocumentMetadata` for the document.
        """
        body = await self._http.get_json(f"/api/documents/{document_id}/metadata/")
        return DocumentMetadata.model_validate(body)

    async def get_notes(self, document_id: int) -> builtins.list[DocumentNote]:
        """List all notes attached to a document.

        Args:
            document_id: ID of the document.

        Returns:
            List of :class:`DocumentNote` objects, oldest first.
        """
        body = await self._http.get_json(f"/api/documents/{document_id}/notes/")
        return [DocumentNote.model_validate(n) for n in body]

    async def get_history(
        self, document_id: int
    ) -> builtins.list[DocumentHistoryEntry]:
        """Fetch the audit history for a document.

        Args:
            document_id: ID of the document.

        Returns:
            List of :class:`DocumentHistoryEntry` objects.
        """
        body = await self._http.get_json(f"/api/documents/{document_id}/history/")
        return [DocumentHistoryEntry.model_validate(h) for h in body]

    async def get_suggestions(self, document_id: int) -> DocumentSuggestions:
        """Fetch classifier suggestions for a document.

        Args:
            document_id: ID of the document.

        Returns:
            :class:`DocumentSuggestions` with tag, correspondent, and type hints.
        """
        body = await self._http.get_json(f"/api/documents/{document_id}/suggestions/")
        return DocumentSuggestions.model_validate(body)

    async def update(self, document_id: int, patch: DocumentPatch) -> Document:
        """Partially update a document via PATCH.

        Args:
            document_id: ID of the document to update.
            patch: Fields to update; unset fields are excluded from the payload.

        Returns:
            The updated Document.
        """
        payload = patch.model_dump(exclude_unset=True, mode="json")
        body = await self._http.patch_json(
            f"/api/documents/{document_id}/", json=payload
        )
        return Document.model_validate(body)

    async def delete(self, document_id: int) -> None:
        """Delete a document by ID.

        Args:
            document_id: ID of the document to delete.
        """
        await self._http.delete(f"/api/documents/{document_id}/")

    async def upload(
        self,
        *,
        filename: str,
        content: bytes,
        title: str | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        tags: Sequence[int] | None = None,
        created: str | None = None,
        archive_serial_number: str | int | None = None,
        custom_fields: Sequence[int] | None = None,
    ) -> UploadTaskAcknowledgement:
        """Upload a new document via multipart form POST.

        Args:
            filename: Original filename to attach to the upload.
            content: Raw document bytes.
            title: Optional title to set on the document.
            correspondent: Optional correspondent ID.
            document_type: Optional document type ID.
            tags: Optional list of tag IDs.
            created: Optional ISO-8601 created date string.
            archive_serial_number: Optional archive serial number.
            custom_fields: Optional list of custom field IDs.

        Returns:
            An :class:`UploadTaskAcknowledgement` containing the task UUID.
        """
        files: dict[str, object] = {
            "document": (filename, content, "application/octet-stream")
        }
        data: dict[str, object] = {}
        if title is not None:
            data["title"] = title
        if correspondent is not None:
            data["correspondent"] = correspondent
        if document_type is not None:
            data["document_type"] = document_type
        if tags is not None:
            data["tags"] = [str(t) for t in tags]
        if created is not None:
            data["created"] = created
        if archive_serial_number is not None:
            data["archive_serial_number"] = str(archive_serial_number)
        if custom_fields is not None:
            data["custom_fields"] = [str(cf) for cf in custom_fields]

        body = await self._http.upload_multipart(
            "/api/documents/post_document/", data=data, files=files
        )
        if isinstance(body, str):
            return UploadTaskAcknowledgement(task_id=body)
        if isinstance(body, dict) and "task_id" in body:
            return UploadTaskAcknowledgement.model_validate(body)
        msg = f"unexpected upload response shape: {body!r}"
        raise TypeError(msg)

    async def bulk_edit(
        self,
        *,
        document_ids: Sequence[int],
        method: BulkEditOperation,
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Perform a bulk edit operation on multiple documents.

        Args:
            document_ids: List of document IDs to act on.
            method: The bulk edit operation to perform.
            parameters: Optional extra parameters for the operation.

        Returns:
            A :class:`BulkEditResult` with the operation result.
        """
        payload: dict[str, object] = {
            "documents": document_ids,
            "method": method.value,
            "parameters": parameters or {},
        }
        body = await self._http.post_json("/api/documents/bulk_edit/", json=payload)
        return BulkEditResult.model_validate(body)

    async def add_note(self, document_id: int, note: str) -> DocumentNote:
        """Add a note to a document.

        Args:
            document_id: ID of the document.
            note: Text content of the note.

        Returns:
            The newly created :class:`DocumentNote`.
        """
        body = await self._http.post_json(
            f"/api/documents/{document_id}/notes/", json={"note": note}
        )
        notes = [DocumentNote.model_validate(n) for n in body]
        if not notes:
            msg = "add_note: empty notes list returned"
            raise RuntimeError(msg)
        return notes[-1]

    async def delete_note(self, document_id: int, note_id: int) -> None:
        """Delete a note from a document.

        Args:
            document_id: ID of the document.
            note_id: ID of the note to delete.
        """
        await self._http.delete(
            f"/api/documents/{document_id}/notes/", params={"id": note_id}
        )
