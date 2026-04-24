"""Tests for list/search content-stripping behaviour."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from paperless_mcp.client import PaperlessClient


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
