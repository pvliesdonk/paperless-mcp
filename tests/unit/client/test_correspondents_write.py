from __future__ import annotations

import json

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.correspondents import CorrespondentsClient
from paperless_mcp.models.correspondent import CorrespondentCreate, CorrespondentPatch


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
async def test_create(correspondents, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.post("/api/correspondents/").mock(
            return_value=httpx.Response(201, json=load_fixture("correspondent.json"))
        )
        r = await correspondents.create(CorrespondentCreate(name="ACME"))
    assert r.id == 1


@pytest.mark.asyncio
async def test_update(correspondents, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.patch("/api/correspondents/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("correspondent.json"))
        )
        r = await correspondents.update(1, CorrespondentPatch(name="Renamed"))
    assert r.id == 1


@pytest.mark.asyncio
async def test_delete(correspondents) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/correspondents/1/").mock(
            return_value=httpx.Response(204)
        )
        await correspondents.delete(1)
    assert route.called


@pytest.mark.asyncio
async def test_bulk_edit(correspondents) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/bulk_edit_objects/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        result = await correspondents.bulk_edit(operation="set_permissions", ids=[1])
    assert result.result == "OK"
    assert (
        json.loads(route.calls.last.request.content)["object_type"] == "correspondents"
    )
