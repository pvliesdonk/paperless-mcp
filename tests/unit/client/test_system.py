from __future__ import annotations
import httpx, pytest, respx
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.system import SystemClient

@pytest.fixture
async def http():
    client = PaperlessHTTP(base_url="http://paperless.test", api_token="t", max_retries=0)
    yield client
    await client.aclose()

@pytest.mark.asyncio
async def test_statistics(http: PaperlessHTTP, load_fixture) -> None:
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/statistics/").mock(return_value=httpx.Response(200, json=load_fixture("statistics.json")))
        s = await system.statistics()
    assert s.documents_total == 1234

@pytest.mark.asyncio
async def test_remote_version(http: PaperlessHTTP, load_fixture) -> None:
    system = SystemClient(http)
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/remote_version/").mock(return_value=httpx.Response(200, json=load_fixture("remote_version.json")))
        v = await system.remote_version()
    assert v.version == "2.7.2"
