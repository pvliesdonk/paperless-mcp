from __future__ import annotations

import json

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.document_types import DocumentTypesClient
from paperless_mcp.models.document_type import DocumentTypeCreate, DocumentTypePatch


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
async def test_create(document_types, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.post("/api/document_types/").mock(
            return_value=httpx.Response(201, json=load_fixture("document_type.json"))
        )
        r = await document_types.create(DocumentTypeCreate(name="Invoice"))
    assert r.id == 3


@pytest.mark.asyncio
async def test_update(document_types, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.patch("/api/document_types/3/").mock(
            return_value=httpx.Response(200, json=load_fixture("document_type.json"))
        )
        r = await document_types.update(3, DocumentTypePatch(name="Renamed"))
    assert r.id == 3
    assert json.loads(route.calls.last.request.content) == {"name": "Renamed"}


@pytest.mark.asyncio
async def test_delete(document_types) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/document_types/3/").mock(
            return_value=httpx.Response(204)
        )
        await document_types.delete(3)
    assert route.called


@pytest.mark.asyncio
async def test_bulk_edit(document_types) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/bulk_edit_objects/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        result = await document_types.bulk_edit(operation="set_permissions", ids=[3])
    assert result.result == "OK"
    assert (
        json.loads(route.calls.last.request.content)["object_type"] == "document_types"
    )
