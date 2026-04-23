from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.custom_fields import CustomFieldsClient


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def custom_fields(http: PaperlessHTTP) -> CustomFieldsClient:
    return CustomFieldsClient(http)


@pytest.mark.asyncio
async def test_list(custom_fields: CustomFieldsClient, load_fixture) -> None:
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("custom_field.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/custom_fields/").mock(
            return_value=httpx.Response(200, json=page)
        )
        result = await custom_fields.list()
    assert result.results[0].name == "Summary"


@pytest.mark.asyncio
async def test_get(custom_fields: CustomFieldsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/custom_fields/2/").mock(
            return_value=httpx.Response(200, json=load_fixture("custom_field.json"))
        )
        cf = await custom_fields.get(2)
    assert cf.id == 2
