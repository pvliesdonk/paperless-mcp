from __future__ import annotations
import httpx, pytest, respx
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.tags import TagsClient

@pytest.fixture
async def http():
    client = PaperlessHTTP(base_url="http://paperless.test", api_token="t", max_retries=0)
    yield client
    await client.aclose()

@pytest.fixture
def tags(http: PaperlessHTTP) -> TagsClient:
    return TagsClient(http)

@pytest.mark.asyncio
async def test_list(tags: TagsClient, load_fixture) -> None:
    page = {"count": 1, "next": None, "previous": None, "results": [load_fixture("tag.json")]}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(return_value=httpx.Response(200, json=page))
        result = await tags.list(page=1, page_size=100, name__icontains="inv")
    params = dict(route.calls.last.request.url.params)
    assert params["name__icontains"] == "inv"
    assert result.results[0].name == "Invoice"

@pytest.mark.asyncio
async def test_get(tags: TagsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tags/1/").mock(return_value=httpx.Response(200, json=load_fixture("tag.json")))
        tag = await tags.get(1)
    assert tag.id == 1
