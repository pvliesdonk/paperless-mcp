"""Tests for the HTTP client base."""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
import respx

from paperless_mcp.client._errors import NotFoundError, UpstreamError
from paperless_mcp.client._http import PaperlessHTTP


@pytest.fixture
async def http() -> AsyncIterator[PaperlessHTTP]:
    client = PaperlessHTTP(
        base_url="http://paperless.test",
        api_token="test-token",
        timeout_seconds=5.0,
        max_retries=2,
    )
    try:
        yield client
    finally:
        await client.aclose()


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
    # The literal protects the version 10 default; fallback has separate tests.
    assert "version=10" in accept


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


@pytest.mark.asyncio
async def test_version_rejection_falls_back_and_is_cached(http: PaperlessHTTP) -> None:
    """A v10 refusal happens before the view; writes can be retried at v9."""
    refusal = {"detail": 'Invalid version in "Accept" header.'}
    async with respx.mock(base_url="http://paperless.test") as mock:
        create = mock.post("/api/tags/").mock(
            side_effect=[
                httpx.Response(406, json=refusal),
                httpx.Response(201, json={"id": 1}),
            ]
        )
        get = mock.get("/api/tags/").mock(return_value=httpx.Response(200, json=[]))
        assert await http.post_json("/api/tags/", json={"name": "x"}) == {"id": 1}
        await http.get_json("/api/tags/")
    assert [call.request.headers["accept"] for call in create.calls] == [
        "application/json; version=10",
        "application/json; version=9",
    ]
    assert create.calls[0].request.content == create.calls[1].request.content
    assert get.calls.last.request.headers["accept"] == "application/json; version=9"


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [b"not json", b"[]", b'{"detail":"other refusal"}'])
async def test_other_406_does_not_downgrade(http: PaperlessHTTP, body: bytes) -> None:
    from paperless_mcp.client._errors import PaperlessAPIError

    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            return_value=httpx.Response(406, content=body)
        )
        with pytest.raises(PaperlessAPIError):
            await http.get_json("/api/tags/")
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_version_fallback_is_bounded(http: PaperlessHTTP) -> None:
    from paperless_mcp.client._errors import PaperlessAPIError

    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tags/").mock(
            return_value=httpx.Response(
                406, json={"detail": 'Invalid version in "Accept" header.'}
            )
        )
        with pytest.raises(PaperlessAPIError):
            await http.get_json("/api/tags/")
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_multipart_version_fallback_preserves_upload(http: PaperlessHTTP) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/documents/post_document/").mock(
            side_effect=[
                httpx.Response(
                    406, json={"detail": 'Invalid version in "Accept" header.'}
                ),
                httpx.Response(200, json="task-id"),
            ]
        )
        result = await http.upload_multipart(
            "/api/documents/post_document/",
            data={"title": "Notes"},
            files={"document": ("notes.md", b"# Notes")},
        )
    assert result == "task-id"
    assert route.call_count == 2
    assert all(b"# Notes" in call.request.content for call in route.calls)
