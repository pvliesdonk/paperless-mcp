from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.system import RemoteVersion, Statistics


class SystemClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def statistics(self) -> Statistics:
        body = await self._http.get_json("/api/statistics/")
        return Statistics.model_validate(body)

    async def remote_version(self) -> RemoteVersion:
        body = await self._http.get_json("/api/remote_version/")
        return RemoteVersion.model_validate(body)
