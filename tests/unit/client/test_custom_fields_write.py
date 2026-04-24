from __future__ import annotations

import json

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.custom_fields import CustomFieldsClient
from paperless_mcp.models.custom_field import (
    CustomFieldCreate,
    CustomFieldDataType,
    CustomFieldPatch,
)


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
async def test_create(custom_fields, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.post("/api/custom_fields/").mock(
            return_value=httpx.Response(201, json=load_fixture("custom_field.json"))
        )
        r = await custom_fields.create(
            CustomFieldCreate(name="Summary", data_type=CustomFieldDataType.LONGTEXT)
        )
    assert r.id == 2


@pytest.mark.asyncio
async def test_update(custom_fields, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.patch("/api/custom_fields/2/").mock(
            return_value=httpx.Response(200, json=load_fixture("custom_field.json"))
        )
        r = await custom_fields.update(2, CustomFieldPatch(name="Renamed"))
    assert r.id == 2
    assert json.loads(route.calls.last.request.content) == {"name": "Renamed"}


@pytest.mark.asyncio
async def test_delete(custom_fields) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/custom_fields/2/").mock(
            return_value=httpx.Response(204)
        )
        await custom_fields.delete(2)
    assert route.called


@pytest.mark.asyncio
async def test_bulk_edit(custom_fields) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/bulk_edit_objects/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        result = await custom_fields.bulk_edit(operation="set_permissions", ids=[2])
    assert result.result == "OK"
    assert (
        json.loads(route.calls.last.request.content)["object_type"] == "custom_fields"
    )
