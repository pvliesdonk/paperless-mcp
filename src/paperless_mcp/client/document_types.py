from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.document_type import DocumentType

class DocumentTypesClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 100, ordering: str | None = None, name__icontains: str | None = None) -> Paginated[DocumentType]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        if name__icontains: params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/document_types/", params=params)
        return Paginated[DocumentType].model_validate(body)

    async def get(self, document_type_id: int) -> DocumentType:
        body = await self._http.get_json(f"/api/document_types/{document_type_id}/")
        return DocumentType.model_validate(body)
