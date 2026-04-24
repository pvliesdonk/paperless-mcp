"""Saved views resource client."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.saved_view import SavedView


class SavedViewsClient:
    """Async operations against ``/api/saved_views/``."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self, *, page: int = 1, page_size: int = 100
    ) -> Paginated[SavedView]:
        """List saved views.

        Args:
            page: Page number (1-based).
            page_size: Number of results per page.

        Returns:
            Paginated list of :class:`SavedView` objects.
        """
        body = await self._http.get_json(
            "/api/saved_views/", params={"page": page, "page_size": page_size}
        )
        return Paginated[SavedView].model_validate(body)

    async def get(self, view_id: int) -> SavedView:
        """Fetch a single saved view by ID.

        Args:
            view_id: ID of the saved view.

        Returns:
            The matching :class:`SavedView`.
        """
        body = await self._http.get_json(f"/api/saved_views/{view_id}/")
        return SavedView.model_validate(body)
