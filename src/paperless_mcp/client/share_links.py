from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.share_link import ShareLink


class ShareLinksClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self, *, page: int = 1, page_size: int = 100, document_id: int | None = None
    ) -> Paginated[ShareLink]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if document_id is not None:
            params["document"] = document_id
        body = await self._http.get_json("/api/share_links/", params=params)
        return Paginated[ShareLink].model_validate(body)

    async def get(self, share_link_id: int) -> ShareLink:
        body = await self._http.get_json(f"/api/share_links/{share_link_id}/")
        return ShareLink.model_validate(body)
