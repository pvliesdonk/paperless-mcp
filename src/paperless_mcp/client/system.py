"""System resource client for Paperless-NGX statistics and version info."""

from __future__ import annotations

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.system import (
    RemoteVersion,
    Statistics,
    UiSettingsResponse,
)


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
        """Fetch the newest Paperless-NGX release published upstream.

        This is an update check, not an identity check: Paperless answers with
        the latest release tag it read from GitHub, and never with the version
        it is itself running.

        Returns:
            :class:`RemoteVersion` with the latest available version and
            whether it is newer than the running one.
        """
        body = await self._http.get_json("/api/remote_version/")
        return RemoteVersion.model_validate(body)

    async def installed_version(self) -> str:
        """Fetch the Paperless-NGX version running on the connected instance.

        Reads ``settings.version`` from ``/api/ui_settings/``, which Paperless
        fills from its own ``__full_version_str__``.  That endpoint needs only
        an authenticated user, unlike ``/api/status/``'s ``pngx_version``,
        which is admin-gated.

        The call is a plain ``GET`` with no body.  Paperless's handler reads
        the calling user's stored UI settings when the row exists and returns
        the envelope; writing them is the ``POST`` on the same path, which this
        client never issues.  [verified: paperless-ngx
        ``src/documents/views.py`` lines 4087-4162 and
        ``UiSettingsViewSerializer`` in ``src/documents/serialisers.py``, whose
        ``settings`` field is ``required=False`` so an empty request body
        validates.]

        Returns:
            The installed version string, e.g. ``"2.20.14"``.
        """
        body = await self._http.get_json("/api/ui_settings/")
        return UiSettingsResponse.model_validate(body).settings.version
