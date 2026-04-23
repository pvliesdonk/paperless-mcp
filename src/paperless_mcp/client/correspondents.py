from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.correspondent import Correspondent

class CorrespondentsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 100, ordering: str | None = None, name__icontains: str | None = None) -> Paginated[Correspondent]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        if name__icontains: params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/correspondents/", params=params)
        return Paginated[Correspondent].model_validate(body)

    async def get(self, correspondent_id: int) -> Correspondent:
        body = await self._http.get_json(f"/api/correspondents/{correspondent_id}/")
        return Correspondent.model_validate(body)
