from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.storage_path import StoragePath

class StoragePathsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 100, ordering: str | None = None) -> Paginated[StoragePath]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        body = await self._http.get_json("/api/storage_paths/", params=params)
        return Paginated[StoragePath].model_validate(body)

    async def get(self, storage_path_id: int) -> StoragePath:
        body = await self._http.get_json(f"/api/storage_paths/{storage_path_id}/")
        return StoragePath.model_validate(body)
