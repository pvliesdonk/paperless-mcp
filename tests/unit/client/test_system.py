from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx
import pytest
import respx

from paperless_mcp.client import AuthError
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.system import SystemClient


@pytest.fixture
async def http() -> AsyncIterator[PaperlessHTTP]:
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_statistics(
    http: PaperlessHTTP, load_fixture: Callable[[str], Any]
) -> None:
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/statistics/").mock(
            return_value=httpx.Response(200, json=load_fixture("statistics.json"))
        )
        s = await system.statistics()
    assert s.documents_total == 1234


@pytest.mark.asyncio
async def test_remote_version(
    http: PaperlessHTTP, load_fixture: Callable[[str], Any]
) -> None:
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/remote_version/").mock(
            return_value=httpx.Response(200, json=load_fixture("remote_version.json"))
        )
        v = await system.remote_version()
    # The endpoint reports the newest release published upstream, not the
    # version of the instance answering — see the RemoteVersion docstring.
    assert v.version == "2.7.2"


@pytest.mark.asyncio
async def test_installed_version(
    http: PaperlessHTTP, load_fixture: Callable[[str], Any]
) -> None:
    """The installed version comes from `settings.version` of /api/ui_settings/."""
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json=load_fixture("ui_settings.json"))
        )
        assert await system.installed_version() == "2.14.7"


@pytest.mark.asyncio
async def test_installed_version_only_reads(
    http: PaperlessHTTP, load_fixture: Callable[[str], Any]
) -> None:
    """The call must be a bodyless GET.

    `/api/ui_settings/` also accepts a POST that writes the calling user's UI
    settings row. This client must never take that path, and must not send a
    request body that Paperless's serializer would have to validate.
    """
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json=load_fixture("ui_settings.json"))
        )
        await system.installed_version()
    assert len(route.calls) == 1
    request = route.calls.last.request
    assert request.method == "GET"
    assert request.content == b""
    assert "content-type" not in request.headers


@pytest.mark.asyncio
async def test_installed_version_rejects_a_body_without_the_version(
    http: PaperlessHTTP,
) -> None:
    """A settings object with no `version` is a malformed answer, not a None.

    `upstream_version_provider` catches the resulting ValueError (pydantic's
    ValidationError derives from it) and degrades to no version.
    """
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json={"settings": {}})
        )
        with pytest.raises(ValueError, match="version"):
            await system.installed_version()


@pytest.mark.asyncio
async def test_installed_version_needs_the_ui_settings_view_permission(
    http: PaperlessHTTP,
) -> None:
    """A token without `documents.view_uisettings` gets 403, raised as AuthError.

    `/api/ui_settings/` is gated by `IsAuthenticated` *and*
    `PaperlessObjectPermissions`, whose `perms_map` maps GET to
    `<app_label>.view_<model_name>`. `/api/remote_version/` has no such gate, so
    this is a real cost of reading the correct endpoint; the upstream-version
    provider treats it as it treats any other failure and reports no version.
    """
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(403, json={"detail": "Insufficient perms"})
        )
        with pytest.raises(AuthError):
            await system.installed_version()
