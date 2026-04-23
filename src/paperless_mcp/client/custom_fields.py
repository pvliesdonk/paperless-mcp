from __future__ import annotations
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.custom_field import CustomField

class CustomFieldsClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(self, *, page: int = 1, page_size: int = 100, ordering: str | None = None) -> Paginated[CustomField]:
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if ordering: params["ordering"] = ordering
        body = await self._http.get_json("/api/custom_fields/", params=params)
        return Paginated[CustomField].model_validate(body)

    async def get(self, field_id: int) -> CustomField:
        body = await self._http.get_json(f"/api/custom_fields/{field_id}/")
        return CustomField.model_validate(body)
