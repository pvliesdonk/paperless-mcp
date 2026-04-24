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
