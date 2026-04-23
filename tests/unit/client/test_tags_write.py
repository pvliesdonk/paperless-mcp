from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.tags import TagsClient
from paperless_mcp.models.tag import TagCreate, TagPatch


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def tags(http: PaperlessHTTP) -> TagsClient:
    return TagsClient(http)


@pytest.mark.asyncio
async def test_create(tags: TagsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.post("/api/tags/").mock(
            return_value=httpx.Response(201, json=load_fixture("tag.json"))
        )
        result = await tags.create(TagCreate(name="New"))
    assert result.id == 1


@pytest.mark.asyncio
async def test_update(tags: TagsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.patch("/api/tags/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("tag.json"))
        )
        result = await tags.update(1, TagPatch(name="Renamed"))
    assert result.id == 1
    import json

    assert json.loads(route.calls.last.request.content) == {"name": "Renamed"}


@pytest.mark.asyncio
async def test_delete(tags: TagsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/tags/1/").mock(return_value=httpx.Response(204))
        await tags.delete(1)
    assert route.called


@pytest.mark.asyncio
async def test_bulk_edit(tags: TagsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/bulk_edit_objects/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        result = await tags.bulk_edit(
            operation="set_permissions", ids=[1, 2], parameters={}
        )
    assert result.result == "OK"
    import json

    body = json.loads(route.calls.last.request.content)
    assert body["object_type"] == "tags"
    assert body["objects"] == [1, 2]
    assert body["operation"] == "set_permissions"
