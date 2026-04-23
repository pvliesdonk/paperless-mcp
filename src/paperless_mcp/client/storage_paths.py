"""Storage paths resource client."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.storage_path import StoragePath


class StoragePathsClient:
    """Async operations against ``/api/storage_paths/``."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self, *, page: int = 1, page_size: int = 100, ordering: str | None = None
    ) -> Paginated[StoragePath]:
        """List storage paths.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field name to order by (prefix with ``-`` for descending).

        Returns:
            Paginated list of :class:`StoragePath` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        body = await self._http.get_json("/api/storage_paths/", params=params)
        return Paginated[StoragePath].model_validate(body)

    async def get(self, storage_path_id: int) -> StoragePath:
        """Fetch a single storage path by ID.

        Args:
            storage_path_id: ID of the storage path.

        Returns:
            The matching :class:`StoragePath`.
        """
        body = await self._http.get_json(f"/api/storage_paths/{storage_path_id}/")
        return StoragePath.model_validate(body)
