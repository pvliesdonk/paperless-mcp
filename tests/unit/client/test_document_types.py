from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.document_types import DocumentTypesClient


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def document_types(http: PaperlessHTTP) -> DocumentTypesClient:
    return DocumentTypesClient(http)


@pytest.mark.asyncio
async def test_list(document_types: DocumentTypesClient, load_fixture) -> None:
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("document_type.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/document_types/").mock(
            return_value=httpx.Response(200, json=page)
        )
        result = await document_types.list()
    assert result.results[0].name == "Invoice"


@pytest.mark.asyncio
async def test_get(document_types: DocumentTypesClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/document_types/3/").mock(
            return_value=httpx.Response(200, json=load_fixture("document_type.json"))
        )
        dt = await document_types.get(3)
    assert dt.id == 3
