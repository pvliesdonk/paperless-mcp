"""Tests for the HTTP client base."""

from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._errors import NotFoundError, UpstreamError
from paperless_mcp.client._http import PaperlessHTTP


@pytest.fixture
def http() -> PaperlessHTTP:
    return PaperlessHTTP(
        base_url="http://paperless.test",
        api_token="test-token",
        timeout_seconds=5.0,
        max_retries=2,
    )


@pytest.mark.asyncio
async def test_auth_header_attached(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            return_value=httpx.Response(200, json={"count": 0, "results": []})
        )
        await http.get_json("/api/tags/")
    assert route.called
    auth = route.calls.last.request.headers["authorization"]
    assert auth == "Token test-token"


@pytest.mark.asyncio
async def test_accept_header_pins_version(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            return_value=httpx.Response(200, json={"count": 0, "results": []})
        )
        await http.get_json("/api/tags/")
    accept = route.calls.last.request.headers["accept"]
    assert "application/json" in accept
    assert "version=" in accept


@pytest.mark.asyncio
async def test_404_raises_not_found(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tags/999/").mock(
            return_value=httpx.Response(404, json={"detail": "Not found."})
        )
        with pytest.raises(NotFoundError):
            await http.get_json("/api/tags/999/")


@pytest.mark.asyncio
async def test_5xx_retries_then_fails(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            return_value=httpx.Response(500, json={"detail": "boom"})
        )
        with pytest.raises(UpstreamError):
            await http.get_json("/api/tags/")
        # initial attempt + 2 retries
        assert route.call_count == 3


@pytest.mark.asyncio
async def test_5xx_then_success(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(200, json={"count": 0, "results": []}),
            ]
        )
        body = await http.get_json("/api/tags/")
    assert route.call_count == 2
    assert body["count"] == 0


@pytest.mark.asyncio
async def test_post_does_not_retry_on_5xx(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/tags/").mock(
            return_value=httpx.Response(500, json={"detail": "boom"})
        )
        with pytest.raises(UpstreamError):
            await http.post_json("/api/tags/", json={"name": "x"})
        assert route.call_count == 1
