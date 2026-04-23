"""Documents resource client for Paperless-NGX."""
from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.document import Document, DocumentHistoryEntry, DocumentMetadata, DocumentNote, DocumentSuggestions

class DocumentsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 25, ordering: str | None = None, tags: list[int] | None = None, correspondent: int | None = None, document_type: int | None = None, storage_path: int | None = None, custom_field: int | None = None) -> Paginated[Document]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        if tags: params["tags__id__in"] = ",".join(str(t) for t in tags)
        if correspondent is not None: params["correspondent__id"] = correspondent
        if document_type is not None: params["document_type__id"] = document_type
        if storage_path is not None: params["storage_path__id"] = storage_path
        if custom_field is not None: params["custom_fields__id"] = custom_field
        body = await self._http.get_json("/api/documents/", params=params)
        return Paginated[Document].model_validate(body)

    async def search(self, query: str, *, page: int = 1, page_size: int = 25, more_like: int | None = None) -> Paginated[Document]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if more_like is not None: params["more_like_id"] = more_like
        if query: params["query"] = query
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

    async def download(self, document_id: int, *, original: bool = False) -> tuple[bytes, str]:
        params = {"original": "true"} if original else None
        return await self._http.stream_bytes(f"/api/documents/{document_id}/download/", params=params)

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
