"""Documents resource client for Paperless-NGX."""

from __future__ import annotations

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


class DocumentsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        ordering: str | None = None,
        tags: list[int] | None = None,
        correspondent: int | None = None,
        document_type: int | None = None,
        storage_path: int | None = None,
        custom_field: int | None = None,
    ) -> Paginated[Document]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        if tags:
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
        return Paginated[Document].model_validate(body)

    async def search(
        self,
        query: str,
        *,
        page: int = 1,
        page_size: int = 25,
        more_like: int | None = None,
    ) -> Paginated[Document]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if more_like is not None:
            params["more_like_id"] = more_like
        if query:
            params["query"] = query
        body = await self._http.get_json("/api/documents/", params=params)
        return Paginated[Document].model_validate(body)

    async def get(self, document_id: int) -> Document:
        body = await self._http.get_json(f"/api/documents/{document_id}/")
        return Document.model_validate(body)

    async def get_content(self, document_id: int) -> str:
        doc = await self.get(document_id)
        return doc.content or ""

    async def get_thumbnail(self, document_id: int) -> tuple[bytes, str]:
        return await self._http.stream_bytes(f"/api/documents/{document_id}/thumb/")

    async def get_preview(self, document_id: int) -> tuple[bytes, str]:
        return await self._http.stream_bytes(f"/api/documents/{document_id}/preview/")

    async def download(
        self, document_id: int, *, original: bool = False
    ) -> tuple[bytes, str]:
        params = {"original": "true"} if original else None
        return await self._http.stream_bytes(
            f"/api/documents/{document_id}/download/", params=params
        )

    async def get_metadata(self, document_id: int) -> DocumentMetadata:
        body = await self._http.get_json(f"/api/documents/{document_id}/metadata/")
        return DocumentMetadata.model_validate(body)

    async def get_notes(self, document_id: int) -> list[DocumentNote]:
        body = await self._http.get_json(f"/api/documents/{document_id}/notes/")
        return [DocumentNote.model_validate(n) for n in body]

    async def get_history(self, document_id: int) -> list[DocumentHistoryEntry]:
        body = await self._http.get_json(f"/api/documents/{document_id}/history/")
        return [DocumentHistoryEntry.model_validate(h) for h in body]

    async def get_suggestions(self, document_id: int) -> DocumentSuggestions:
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
        tags: list[int] | None = None,
        created: str | None = None,
        archive_serial_number: str | int | None = None,
        custom_fields: list[int] | None = None,
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
        files = {"document": (filename, content, "application/octet-stream")}
        data: dict[str, object] = {}
        if title is not None:
            data["title"] = title
        if correspondent is not None:
            data["correspondent"] = correspondent
        if document_type is not None:
            data["document_type"] = document_type
        if tags:
            data["tags"] = [str(t) for t in tags]
        if created is not None:
            data["created"] = created
        if archive_serial_number is not None:
            data["archive_serial_number"] = str(archive_serial_number)
        if custom_fields:
            data["custom_fields"] = [str(cf) for cf in custom_fields]

        response = await self._http._client.request(
            "POST",
            "/api/documents/post_document/",
            data=data,
            files=files,
        )
        if not response.is_success:
            from paperless_mcp.client._errors import error_from_response

            raise error_from_response(response)

        body = response.json()
        if isinstance(body, str):
            return UploadTaskAcknowledgement(task_id=body)
        if isinstance(body, dict) and "task_id" in body:
            return UploadTaskAcknowledgement.model_validate(body)
        msg = f"unexpected upload response shape: {body!r}"
        raise TypeError(msg)

    async def bulk_edit(
        self,
        *,
        document_ids: list[int],
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
        return notes[0]

    async def delete_note(self, document_id: int, note_id: int) -> None:
        """Delete a note from a document.

        Args:
            document_id: ID of the document.
            note_id: ID of the note to delete.
        """
        await self._http.delete(f"/api/documents/{document_id}/notes/?id={note_id}")
