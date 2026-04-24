from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.saved_views import SavedViewsClient
from paperless_mcp.client.share_links import ShareLinksClient
from paperless_mcp.client.storage_paths import StoragePathsClient


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_storage_paths_list(http: PaperlessHTTP, load_fixture) -> None:
    sp = StoragePathsClient(http)
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("storage_path.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/storage_paths/").mock(
            return_value=httpx.Response(200, json=page)
        )
        r = await sp.list()
    assert r.results[0].id == 2


@pytest.mark.asyncio
async def test_storage_paths_get(http: PaperlessHTTP, load_fixture) -> None:
    sp = StoragePathsClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/storage_paths/2/").mock(
            return_value=httpx.Response(200, json=load_fixture("storage_path.json"))
        )
        r = await sp.get(2)
    assert r.name == "Invoices by Year"


@pytest.mark.asyncio
async def test_saved_views_list(http: PaperlessHTTP, load_fixture) -> None:
    sv = SavedViewsClient(http)
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("saved_view.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/saved_views/").mock(return_value=httpx.Response(200, json=page))
        r = await sv.list()
    assert r.results[0].name == "Inbox"


@pytest.mark.asyncio
async def test_saved_views_get(http: PaperlessHTTP, load_fixture) -> None:
    sv = SavedViewsClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/saved_views/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("saved_view.json"))
        )
        r = await sv.get(1)
    assert r.id == 1


@pytest.mark.asyncio
async def test_share_links_list(http: PaperlessHTTP, load_fixture) -> None:
    sl = ShareLinksClient(http)
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("share_link.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/share_links/").mock(
            return_value=httpx.Response(200, json=page)
        )
        r = await sl.list(document_id=42)
    assert r.results[0].id == 5
    assert dict(route.calls.last.request.url.params)["document"] == "42"


@pytest.mark.asyncio
async def test_share_links_get(http: PaperlessHTTP, load_fixture) -> None:
    sl = ShareLinksClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/share_links/5/").mock(
            return_value=httpx.Response(200, json=load_fixture("share_link.json"))
        )
        r = await sl.get(5)
    assert r.id == 5
