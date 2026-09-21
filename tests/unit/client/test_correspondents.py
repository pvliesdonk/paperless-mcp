from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.correspondents import CorrespondentsClient


@pytest.fixture
async def http() -> AsyncIterator[PaperlessHTTP]:
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def correspondents(http: PaperlessHTTP) -> CorrespondentsClient:
    return CorrespondentsClient(http)


@pytest.mark.asyncio
async def test_list(
    correspondents: CorrespondentsClient, load_fixture: Callable[[str], Any]
) -> None:
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("correspondent.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/correspondents/").mock(
            return_value=httpx.Response(200, json=page)
        )
        result = await correspondents.list()
    assert result.results[0].name == "ACME Corporation"


@pytest.mark.asyncio
async def test_list_asks_for_last_correspondence(
    correspondents: CorrespondentsClient,
) -> None:
    """Paperless annotates ``last_correspondence`` on a list only when asked (#172).

    Without the query parameter the key is absent from every row, and
    ``ordering=last_correspondence`` answers ``500``.  Any non-empty value
    switches the annotation on, so the client always sends one.
    """
    page: dict[str, Any] = {"count": 0, "next": None, "previous": None, "results": []}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/correspondents/").mock(
            return_value=httpx.Response(200, json=page)
        )
        await correspondents.list(ordering="-last_correspondence")
    params = route.calls.last.request.url.params
    assert params["last_correspondence"] == "true"
    assert params["ordering"] == "-last_correspondence"


@pytest.mark.asyncio
async def test_get(
    correspondents: CorrespondentsClient, load_fixture: Callable[[str], Any]
) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/correspondents/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("correspondent.json"))
        )
        c = await correspondents.get(1)
    assert c.id == 1
