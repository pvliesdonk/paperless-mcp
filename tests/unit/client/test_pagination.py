"""Tests for the internal pagination helper."""

from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP


@pytest.mark.asyncio
async def test_paginate_walks_all_pages() -> None:
    http = PaperlessHTTP(
        base_url="http://paperless.test",
        api_token="t",
        max_retries=0,
    )
    page1 = {
        "count": 3,
        "next": "http://paperless.test/api/tags/?page=2",
        "previous": None,
        "results": [{"id": 1}, {"id": 2}],
    }
    page2 = {
        "count": 3,
        "next": None,
        "previous": "http://paperless.test/api/tags/?page=1",
        "results": [{"id": 3}],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tags/", params={"page_size": "100"}).mock(
            return_value=httpx.Response(200, json=page1)
        )
        mock.get("/api/tags/", params={"page": "2"}).mock(
            return_value=httpx.Response(200, json=page2)
        )
        collected = [item async for item in http.paginate("/api/tags/")]
    assert [c["id"] for c in collected] == [1, 2, 3]
    await http.aclose()


@pytest.mark.asyncio
async def test_paginate_respects_limit() -> None:
    http = PaperlessHTTP(
        base_url="http://paperless.test",
        api_token="t",
        max_retries=0,
    )
    page1 = {
        "count": 100,
        "next": "http://paperless.test/api/tags/?page=2",
        "previous": None,
        "results": [{"id": i} for i in range(50)],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tags/").mock(return_value=httpx.Response(200, json=page1))
        collected = [item async for item in http.paginate("/api/tags/", limit=5)]
    assert len(collected) == 5
    await http.aclose()
