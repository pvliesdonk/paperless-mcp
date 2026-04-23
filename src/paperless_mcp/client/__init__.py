"""Paperless-NGX REST client."""
from __future__ import annotations
from types import TracebackType
from paperless_mcp.client._errors import AuthError, ConflictError, NotFoundError, PaperlessAPIError, RateLimitError, UpstreamError, ValidationError
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.correspondents import CorrespondentsClient
from paperless_mcp.client.custom_fields import CustomFieldsClient
from paperless_mcp.client.document_types import DocumentTypesClient
from paperless_mcp.client.documents import DocumentsClient
from paperless_mcp.client.saved_views import SavedViewsClient
from paperless_mcp.client.share_links import ShareLinksClient
from paperless_mcp.client.storage_paths import StoragePathsClient
from paperless_mcp.client.system import SystemClient
from paperless_mcp.client.tags import TagsClient
from paperless_mcp.client.tasks import TasksClient

class PaperlessClient:
    """High-level async client aggregating every resource client."""

    def __init__(self, *, base_url: str, api_token: str, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        self._http = PaperlessHTTP(base_url=base_url, api_token=api_token, timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.documents = DocumentsClient(self._http)
        self.tags = TagsClient(self._http)
        self.correspondents = CorrespondentsClient(self._http)
        self.document_types = DocumentTypesClient(self._http)
        self.custom_fields = CustomFieldsClient(self._http)
        self.storage_paths = StoragePathsClient(self._http)
        self.saved_views = SavedViewsClient(self._http)
        self.share_links = ShareLinksClient(self._http)
        self.tasks = TasksClient(self._http)
        self.system = SystemClient(self._http)

    @property
    def http(self) -> PaperlessHTTP:
        return self._http

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "PaperlessClient":
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        await self.aclose()

__all__ = [
    "AuthError", "ConflictError", "NotFoundError", "PaperlessAPIError",
    "PaperlessClient", "RateLimitError", "UpstreamError", "ValidationError",
]
