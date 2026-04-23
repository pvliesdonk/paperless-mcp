"""Correspondents resource client."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.correspondent import (
    Correspondent,
    CorrespondentCreate,
    CorrespondentPatch,
)


class CorrespondentsClient:
    """Async operations against ``/api/correspondents/``."""

    _OBJECT_TYPE = "correspondents"

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[Correspondent]:
        """List correspondents with optional filtering.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field to order by.
            name__icontains: Filter correspondents whose name contains this string.

        Returns:
            A paginated list of :class:`Correspondent` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        if name__icontains:
            params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/correspondents/", params=params)
        return Paginated[Correspondent].model_validate(body)

    async def get(self, correspondent_id: int) -> Correspondent:
        """Fetch a single correspondent by ID.

        Args:
            correspondent_id: ID of the correspondent to fetch.

        Returns:
            The :class:`Correspondent` with the given ID.
        """
        body = await self._http.get_json(f"/api/correspondents/{correspondent_id}/")
        return Correspondent.model_validate(body)

    async def create(self, body: CorrespondentCreate) -> Correspondent:
        """Create a new correspondent.

        Args:
            body: Correspondent creation payload.

        Returns:
            The newly created :class:`Correspondent`.
        """
        payload = body.model_dump(exclude_unset=True, mode="json")
        response = await self._http.post_json("/api/correspondents/", json=payload)
        return Correspondent.model_validate(response)

    async def update(
        self, correspondent_id: int, patch: CorrespondentPatch
    ) -> Correspondent:
        """Partially update a correspondent via PATCH.

        Args:
            correspondent_id: ID of the correspondent to update.
            patch: Fields to update; unset fields are excluded from the payload.

        Returns:
            The updated :class:`Correspondent`.
        """
        payload = patch.model_dump(exclude_unset=True, mode="json")
        response = await self._http.patch_json(
            f"/api/correspondents/{correspondent_id}/", json=payload
        )
        return Correspondent.model_validate(response)

    async def delete(self, correspondent_id: int) -> None:
        """Delete a correspondent by ID.

        Args:
            correspondent_id: ID of the correspondent to delete.
        """
        await self._http.delete(f"/api/correspondents/{correspondent_id}/")

    async def bulk_edit(
        self,
        *,
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Perform a bulk edit operation on multiple correspondents.

        Args:
            operation: The operation to perform (e.g. ``"set_permissions"``).
            ids: List of correspondent IDs to act on.
            parameters: Optional extra parameters for the operation.

        Returns:
            A :class:`BulkEditResult` with the operation result.
        """
        payload: dict[str, object] = {
            "object_type": self._OBJECT_TYPE,
            "objects": ids,
            "operation": operation,
            "parameters": parameters or {},
        }
        body = await self._http.post_json("/api/bulk_edit_objects/", json=payload)
        return BulkEditResult.model_validate(body)
