"""Tests for list/search content-stripping behaviour."""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from paperless_mcp.client import PaperlessClient
from paperless_mcp.client.documents import _LISTING_FIELDS

_OPENAPI = (
    Path(__file__).resolve().parents[3]
    / "docs/design/reference/paperless-openapi-3.1.3.json.gz"
)
# Accepted on write, never returned, so absent from the response schema.
_WRITE_ONLY = {"set_permissions", "remove_inbox_tags"}


@pytest.fixture
def _documents_page() -> dict[str, Any]:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "all": [42],
        "results": [
            {
                "id": 42,
                "title": "Big PDF",
                "content": "A" * 50_000,
                "created": "2026-01-01T00:00:00Z",
                "tags": [],
            }
        ],
    }


@pytest.mark.asyncio
async def test_list_strips_content_by_default(
    _documents_page: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.list()
        finally:
            await c.aclose()
    assert result.results[0].content is None


@pytest.mark.asyncio
async def test_list_keeps_content_when_include_content_true(
    _documents_page: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.list(include_content=True)
        finally:
            await c.aclose()
    assert result.results[0].content == "A" * 50_000


@pytest.mark.asyncio
async def test_search_strips_content_by_default(
    _documents_page: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.search("foo")
        finally:
            await c.aclose()
    assert result.results[0].content is None


@pytest.mark.asyncio
async def test_search_keeps_content_when_include_content_true(
    _documents_page: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.search("foo", include_content=True)
        finally:
            await c.aclose()
    assert result.results[0].content == "A" * 50_000


@pytest.fixture
def _documents_page_with_heavy_fields() -> dict[str, Any]:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "all": [27],
        "results": [
            {
                "id": 27,
                "title": "SABSA summary doc",
                "content": "B" * 10_000,
                "created": "2026-01-01T00:00:00Z",
                "tags": [],
                "notes": [
                    {
                        "id": 9,
                        "note": "N" * 2_000,
                        "created": "2026-02-01T00:00:00Z",
                        "user": {"id": 3, "username": "alice"},
                    }
                ],
                "custom_fields": [
                    {"field": 4, "value": "L" * 1_500},
                    {"field": 5, "value": 42},
                ],
            }
        ],
    }


@pytest.mark.asyncio
async def test_list_strips_notes_and_custom_field_values_by_default(
    _documents_page_with_heavy_fields: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page_with_heavy_fields)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.list()
        finally:
            await c.aclose()
    doc = result.results[0]
    # Heavy text dropped.
    assert doc.notes[0].note is None
    assert doc.custom_fields[0].value is None
    assert doc.custom_fields[1].value is None
    # Metadata refs retained — callers can still detect presence / dereference.
    assert doc.notes[0].id == 9
    assert doc.notes[0].user == 3
    assert doc.custom_fields[0].field == 4
    assert doc.custom_fields[1].field == 5


@pytest.mark.asyncio
async def test_list_strips_heavy_fields_even_when_include_content_true(
    _documents_page_with_heavy_fields: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    # include_content=True retains OCR content but notes/custom_field values
    # are always stripped on list responses — callers must use single-document
    # endpoints to fetch them.
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page_with_heavy_fields)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.list(include_content=True)
        finally:
            await c.aclose()
    doc = result.results[0]
    assert doc.content == "B" * 10_000
    assert doc.notes[0].note is None
    assert doc.custom_fields[0].value is None


@pytest.mark.asyncio
async def test_search_strips_notes_and_custom_field_values_by_default(
    _documents_page_with_heavy_fields: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page_with_heavy_fields)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.search("foo")
        finally:
            await c.aclose()
    doc = result.results[0]
    assert doc.notes[0].note is None
    assert doc.custom_fields[0].value is None
    assert doc.notes[0].id == 9
    assert doc.custom_fields[0].field == 4


@pytest.mark.asyncio
async def test_search_strips_heavy_fields_even_when_include_content_true(
    _documents_page_with_heavy_fields: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    # Mirror of the list() test — search() must also keep notes/custom_field
    # values stripped when the caller opts into full OCR content.
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page_with_heavy_fields)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.search("foo", include_content=True)
        finally:
            await c.aclose()
    doc = result.results[0]
    assert doc.content == "B" * 10_000
    assert doc.notes[0].note is None
    assert doc.custom_fields[0].value is None


@pytest.mark.asyncio
async def test_list_normalises_upstream_next_url(
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    page = {
        "count": 2,
        "next": "http://paperless-ngx:8000/api/documents/?page=2",
        "previous": None,
        "results": [
            {
                "id": 1,
                "title": "T",
                "content": "x",
                "created": "2026-01-01T00:00:00Z",
                "tags": [],
            }
        ],
    }
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(return_value=httpx.Response(200, json=page))
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.list()
        finally:
            await c.aclose()
    # Upstream hostname must not leak into the MCP response.
    assert result.next == "page=2"
    assert result.previous is None


def _projected_page(**extra: Any) -> dict[str, Any]:
    """A list body as Paperless answers a ``fields`` projection without content."""
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 42,
                "title": "Big PDF",
                "created": "2026-01-01T00:00:00Z",
                "tags": [],
                "mime_type": "application/pdf",
                **extra,
            }
        ],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("call", ["list", "search"])
async def test_content_is_left_out_of_the_request_by_default(
    call: str,
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    """Paperless can project fields but not exclude one (#164).

    Naming every field but ``content`` keeps the OCR text out of the response
    itself, not only out of the result the tool returns.
    """
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_projected_page())
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            if call == "list":
                result = await c.documents.list()
            else:
                result = await c.documents.search("invoice")
        finally:
            await c.aclose()
    fields = route.calls.last.request.url.params["fields"].split(",")
    assert "content" not in fields
    # Fields the Document model does not declare still reach the caller.
    assert {"id", "title", "notes", "custom_fields", "mime_type", "versions"} <= set(
        fields
    )
    assert result.results[0].content is None
    assert result.results[0].model_extra is not None
    assert result.results[0].model_extra["mime_type"] == "application/pdf"


@pytest.mark.asyncio
@pytest.mark.parametrize("call", ["list", "search"])
async def test_include_content_sends_no_projection(
    call: str,
    _documents_page: dict[str, Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_documents_page)
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            if call == "list":
                result = await c.documents.list(include_content=True)
            else:
                result = await c.documents.search("invoice", include_content=True)
        finally:
            await c.aclose()
    assert "fields" not in route.calls.last.request.url.params
    assert result.results[0].content == "A" * 50_000


@pytest.mark.asyncio
async def test_search_hit_survives_the_projection(
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    """Paperless adds ``__search_hit__`` after projecting, so it stays."""
    hit = {"score": 1.5, "highlights": "<b>x</b>", "rank": 0}
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=_projected_page(__search_hit__=hit))
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            result = await c.documents.search("invoice")
        finally:
            await c.aclose()
    assert result.results[0].model_extra is not None
    assert result.results[0].model_extra["__search_hit__"] == hit


def test_listing_fields_are_the_3_1_3_document_schema_minus_content() -> None:
    """The projection names what Paperless 3.1.3 returns for a document.

    A field missing here is missing from every list row, so the constant is
    pinned to the ``Document`` response schema shipped with the references.
    """
    schema = json.loads(gzip.decompress(_OPENAPI.read_bytes()))
    returned = set(schema["components"]["schemas"]["Document"]["properties"])
    assert set(_LISTING_FIELDS) - _WRITE_ONLY == returned - {"content"}
