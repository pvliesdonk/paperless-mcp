from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from typing import Any

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
async def http() -> AsyncIterator[PaperlessHTTP]:
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def custom_fields(http: PaperlessHTTP) -> CustomFieldsClient:
    return CustomFieldsClient(http)


@pytest.mark.asyncio
async def test_create(
    custom_fields: CustomFieldsClient, load_fixture: Callable[[str], Any]
) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.post("/api/custom_fields/").mock(
            return_value=httpx.Response(201, json=load_fixture("custom_field.json"))
        )
        r = await custom_fields.create(
            CustomFieldCreate(name="Summary", data_type=CustomFieldDataType.LONGTEXT)
        )
    assert r.id == 2


_SELECT_OPTIONS = [{"id": "abc", "label": "Low"}, {"id": "def", "label": "High"}]


def _select_field() -> dict[str, Any]:
    return {
        "id": 7,
        "name": "Priority",
        "data_type": "select",
        "extra_data": {"select_options": _SELECT_OPTIONS},
    }


@pytest.mark.asyncio
async def test_update(
    custom_fields: CustomFieldsClient, load_fixture: Callable[[str], Any]
) -> None:
    field = load_fixture("custom_field.json")
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/custom_fields/2/").mock(
            return_value=httpx.Response(200, json=field)
        )
        route = mock.patch("/api/custom_fields/2/").mock(
            return_value=httpx.Response(200, json=field)
        )
        r = await custom_fields.update(2, CustomFieldPatch(name="Renamed"))
    assert r.id == 2
    assert json.loads(route.calls.last.request.content) == {"name": "Renamed"}


@pytest.mark.asyncio
async def test_update_select_field_resends_current_options(
    custom_fields: CustomFieldsClient,
) -> None:
    """A name-only patch of a select field carries its current options (#171).

    Paperless validates ``extra_data.select_options`` on every update of a
    select field, so the bare ``{"name": ...}`` body answers ``400``.  The
    options go back with their ids, which keeps every option and the document
    values that reference it.
    """
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/custom_fields/7/").mock(
            return_value=httpx.Response(200, json=_select_field())
        )
        route = mock.patch("/api/custom_fields/7/").mock(
            return_value=httpx.Response(
                200, json={**_select_field(), "name": "Renamed"}
            )
        )
        r = await custom_fields.update(7, CustomFieldPatch(name="Renamed"))
    assert r.name == "Renamed"
    assert json.loads(route.calls.last.request.content) == {
        "name": "Renamed",
        "extra_data": {"select_options": _SELECT_OPTIONS},
    }


@pytest.mark.asyncio
async def test_update_with_extra_data_skips_the_read(
    custom_fields: CustomFieldsClient,
) -> None:
    """A patch that names ``extra_data`` is sent as given, with no extra read."""
    options = [{"id": "abc", "label": "Renamed"}]
    async with respx.mock(
        base_url="http://paperless.test", assert_all_called=False
    ) as mock:
        get_route = mock.get("/api/custom_fields/7/").mock(
            return_value=httpx.Response(200, json=_select_field())
        )
        route = mock.patch("/api/custom_fields/7/").mock(
            return_value=httpx.Response(200, json=_select_field())
        )
        await custom_fields.update(
            7, CustomFieldPatch(extra_data={"select_options": options})
        )
    assert not get_route.called
    assert json.loads(route.calls.last.request.content) == {
        "extra_data": {"select_options": options}
    }


@pytest.mark.asyncio
async def test_delete(custom_fields: CustomFieldsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/custom_fields/2/").mock(
            return_value=httpx.Response(204)
        )
        await custom_fields.delete(2)
    assert route.called


def test_bulk_edit_method_does_not_exist(
    custom_fields: CustomFieldsClient,
) -> None:
    """Paperless rejects ``object_type=custom_fields`` on
    ``/api/bulk_edit_objects/``, so no ``bulk_edit`` method is exposed.
    """
    assert not hasattr(custom_fields, "bulk_edit")
