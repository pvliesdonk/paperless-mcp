"""System resource client for Paperless-NGX statistics and version info.

Which Paperless endpoint answers which version question, and what each costs in
permissions, is recorded in
``docs/design/reference/paperless-version-endpoints.md``.  Read it before
changing which endpoint either version method reads.
"""

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
        fills from its own ``__full_version_str__``.

        The endpoint is not unconditionally reachable: its permission classes
        are ``IsAuthenticated`` plus ``PaperlessObjectPermissions``, whose
        ``perms_map`` maps ``GET`` to ``<app_label>.view_<model_name>``, so the
        token's user needs ``documents.view_uisettings``.  A superuser has it;
        a narrowly-scoped service account may not, and then Paperless answers
        ``403``, which this client raises as
        :class:`~paperless_mcp.client.AuthError`.  Callers that treat the
        version as optional enrichment degrade rather than fail — see
        :func:`paperless_mcp.domain.upstream_version_provider`.
        ``/api/status/``'s ``pngx_version`` is stricter still: it is gated on
        the system-status permission and answers ``403`` without it.
        [verified: paperless-ngx ``src/documents/permissions.py``
        ``PaperlessObjectPermissions.perms_map`` and ``src/documents/views.py``
        ``SystemStatusView`` at ae9529551d17]

        The call is a plain ``GET`` with no body.  Paperless's handler reads
        the calling user's stored UI settings when the row exists and returns
        the envelope; writing them is the ``POST`` on the same path, which this
        client never issues.  [verified: paperless-ngx
        ``src/documents/views.py`` ``UiSettingsView.get`` and
        ``UiSettingsViewSerializer`` in ``src/documents/serialisers.py``, whose
        ``settings`` field is ``required=False`` so an empty request body
        validates — both at ae9529551d17.]

        Returns:
            The installed version string, e.g. ``"2.20.14"``.
        """
        body = await self._http.get_json("/api/ui_settings/")
        return UiSettingsResponse.model_validate(body).settings.version
