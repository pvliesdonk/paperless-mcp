from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.correspondents import CorrespondentsClient


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def correspondents(http: PaperlessHTTP) -> CorrespondentsClient:
    return CorrespondentsClient(http)


@pytest.mark.asyncio
async def test_list(correspondents: CorrespondentsClient, load_fixture) -> None:
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
async def test_get(correspondents: CorrespondentsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/correspondents/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("correspondent.json"))
        )
        c = await correspondents.get(1)
    assert c.id == 1
