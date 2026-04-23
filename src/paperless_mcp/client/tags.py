"""Tags resource client."""

from __future__ import annotations

from collections.abc import Sequence

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.tag import Tag, TagCreate, TagPatch


class TagsClient:
    """Async operations against ``/api/tags/``."""

    _OBJECT_TYPE = "tags"

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[Tag]:
        """List tags with optional filtering.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field to order by.
            name__icontains: Filter tags whose name contains this string.

        Returns:
            A paginated list of :class:`Tag` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        if name__icontains:
            params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/tags/", params=params)
        return Paginated[Tag].model_validate(body)

    async def get(self, tag_id: int) -> Tag:
        """Fetch a single tag by ID.

        Args:
            tag_id: ID of the tag to fetch.

        Returns:
            The :class:`Tag` with the given ID.
        """
        body = await self._http.get_json(f"/api/tags/{tag_id}/")
        return Tag.model_validate(body)

    async def create(self, body: TagCreate) -> Tag:
        """Create a new tag.

        Args:
            body: Tag creation payload.

        Returns:
            The newly created :class:`Tag`.
        """
        payload = body.model_dump(exclude_unset=True, mode="json")
        response = await self._http.post_json("/api/tags/", json=payload)
        return Tag.model_validate(response)

    async def update(self, tag_id: int, patch: TagPatch) -> Tag:
        """Partially update a tag via PATCH.

        Args:
            tag_id: ID of the tag to update.
            patch: Fields to update; unset fields are excluded from the payload.

        Returns:
            The updated :class:`Tag`.
        """
        payload = patch.model_dump(exclude_unset=True, mode="json")
        response = await self._http.patch_json(f"/api/tags/{tag_id}/", json=payload)
        return Tag.model_validate(response)

    async def delete(self, tag_id: int) -> None:
        """Delete a tag by ID.

        Args:
            tag_id: ID of the tag to delete.
        """
        await self._http.delete(f"/api/tags/{tag_id}/")

    async def bulk_edit(
        self,
        *,
        operation: str,
        ids: Sequence[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Perform a bulk edit operation on multiple tags.

        Args:
            operation: The operation to perform (e.g. ``"set_permissions"``).
            ids: List of tag IDs to act on.
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
