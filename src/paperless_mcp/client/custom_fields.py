"""Custom fields resource client."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.custom_field import (
    CustomField,
    CustomFieldCreate,
    CustomFieldPatch,
)


class CustomFieldsClient:
    """Async operations against ``/api/custom_fields/``.

    No ``bulk_edit`` method: Paperless-NGX's ``/api/bulk_edit_objects/``
    endpoint does not accept ``object_type=custom_fields`` (see
    ``BulkEditObjectsSerializer`` in paperless-ngx upstream — the choices are
    ``tags``, ``correspondents``, ``document_types``, ``storage_paths``).
    """

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        ordering: str | None = None,
    ) -> Paginated[CustomField]:
        """List custom fields with optional ordering.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field to order by.

        Returns:
            A paginated list of :class:`CustomField` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        body = await self._http.get_json("/api/custom_fields/", params=params)
        return Paginated[CustomField].model_validate(body)

    async def get(self, field_id: int) -> CustomField:
        """Fetch a single custom field by ID.

        Args:
            field_id: ID of the custom field to fetch.

        Returns:
            The :class:`CustomField` with the given ID.
        """
        body = await self._http.get_json(f"/api/custom_fields/{field_id}/")
        return CustomField.model_validate(body)

    async def create(self, body: CustomFieldCreate) -> CustomField:
        """Create a new custom field.

        Args:
            body: Custom field creation payload.

        Returns:
            The newly created :class:`CustomField`.
        """
        payload = body.model_dump(exclude_unset=True, mode="json")
        response = await self._http.post_json("/api/custom_fields/", json=payload)
        return CustomField.model_validate(response)

    async def update(self, field_id: int, patch: CustomFieldPatch) -> CustomField:
        """Partially update a custom field via PATCH.

        Args:
            field_id: ID of the custom field to update.
            patch: Fields to update; unset fields are excluded from the payload.

        Returns:
            The updated :class:`CustomField`.
        """
        payload = patch.model_dump(exclude_unset=True, mode="json")
        response = await self._http.patch_json(
            f"/api/custom_fields/{field_id}/", json=payload
        )
        return CustomField.model_validate(response)

    async def delete(self, field_id: int) -> None:
        """Delete a custom field by ID.

        Args:
            field_id: ID of the custom field to delete.
        """
        await self._http.delete(f"/api/custom_fields/{field_id}/")
