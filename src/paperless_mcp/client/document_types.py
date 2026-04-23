"""Document types resource client."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import BulkEditResult, Paginated
from paperless_mcp.models.document_type import (
    DocumentType,
    DocumentTypeCreate,
    DocumentTypePatch,
)


class DocumentTypesClient:
    """Async operations against ``/api/document_types/``."""

    _OBJECT_TYPE = "document_types"

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        ordering: str | None = None,
        name__icontains: str | None = None,
    ) -> Paginated[DocumentType]:
        """List document types with optional filtering.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.
            ordering: Field to order by.
            name__icontains: Filter document types whose name contains this string.

        Returns:
            A paginated list of :class:`DocumentType` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering:
            params["ordering"] = ordering
        if name__icontains:
            params["name__icontains"] = name__icontains
        body = await self._http.get_json("/api/document_types/", params=params)
        return Paginated[DocumentType].model_validate(body)

    async def get(self, document_type_id: int) -> DocumentType:
        """Fetch a single document type by ID.

        Args:
            document_type_id: ID of the document type to fetch.

        Returns:
            The :class:`DocumentType` with the given ID.
        """
        body = await self._http.get_json(f"/api/document_types/{document_type_id}/")
        return DocumentType.model_validate(body)

    async def create(self, body: DocumentTypeCreate) -> DocumentType:
        """Create a new document type.

        Args:
            body: Document type creation payload.

        Returns:
            The newly created :class:`DocumentType`.
        """
        payload = body.model_dump(exclude_unset=True, mode="json")
        response = await self._http.post_json("/api/document_types/", json=payload)
        return DocumentType.model_validate(response)

    async def update(
        self, document_type_id: int, patch: DocumentTypePatch
    ) -> DocumentType:
        """Partially update a document type via PATCH.

        Args:
            document_type_id: ID of the document type to update.
            patch: Fields to update; unset fields are excluded from the payload.

        Returns:
            The updated :class:`DocumentType`.
        """
        payload = patch.model_dump(exclude_unset=True, mode="json")
        response = await self._http.patch_json(
            f"/api/document_types/{document_type_id}/", json=payload
        )
        return DocumentType.model_validate(response)

    async def delete(self, document_type_id: int) -> None:
        """Delete a document type by ID.

        Args:
            document_type_id: ID of the document type to delete.
        """
        await self._http.delete(f"/api/document_types/{document_type_id}/")

    async def bulk_edit(
        self,
        *,
        operation: str,
        ids: list[int],
        parameters: dict[str, object] | None = None,
    ) -> BulkEditResult:
        """Perform a bulk edit operation on multiple document types.

        Args:
            operation: The operation to perform (e.g. ``"set_permissions"``).
            ids: List of document type IDs to act on.
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
