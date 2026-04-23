"""System resource client for Paperless-NGX statistics and version info."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.system import RemoteVersion, Statistics


class SystemClient:
    """Async operations against Paperless-NGX system endpoints."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def statistics(self) -> Statistics:
        """Fetch document and storage statistics from Paperless-NGX.

        Returns:
            :class:`Statistics` with counts and storage metrics.
        """
        body = await self._http.get_json("/api/statistics/")
        return Statistics.model_validate(body)

    async def remote_version(self) -> RemoteVersion:
        """Fetch the latest available Paperless-NGX version from the remote.

        Returns:
            :class:`RemoteVersion` with current and latest version strings.
        """
        body = await self._http.get_json("/api/remote_version/")
        return RemoteVersion.model_validate(body)
