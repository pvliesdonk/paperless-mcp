from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.tag import Tag

class TagsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 100, ordering: str | None = None, name__icontains: str | None = None) -> Paginated[Tag]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        if name__icontains: params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/tags/", params=params)
        return Paginated[Tag].model_validate(body)

    async def get(self, tag_id: int) -> Tag:
        body = await self._http.get_json(f"/api/tags/{tag_id}/")
        return Tag.model_validate(body)
