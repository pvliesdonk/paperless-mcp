"""Tests for DocumentsClient read operations."""

from __future__ import annotations

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.documents import DocumentsClient


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def documents(http: PaperlessHTTP) -> DocumentsClient:
    return DocumentsClient(http)


@pytest.mark.asyncio
async def test_list_documents_passes_filters(
    documents: DocumentsClient, load_fixture
) -> None:
    page = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [load_fixture("document_minimal.json")],
    }
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=page)
        )
        result = await documents.list(
            page=2, page_size=50, tags=[1, 2], correspondent=7, document_type=3
        )
    params = dict(route.calls.last.request.url.params)
    assert params["page"] == "2"
    assert params["page_size"] == "50"
    assert params["tags__id__in"] == "1,2"
    assert params["correspondent__id"] == "7"
    assert params["document_type__id"] == "3"
    assert result.results[0].id == 1


@pytest.mark.asyncio
async def test_search_uses_query_param(
    documents: DocumentsClient, load_fixture
) -> None:
    page = {"count": 0, "next": None, "previous": None, "results": []}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=page)
        )
        await documents.search("hello world")
    assert dict(route.calls.last.request.url.params)["query"] == "hello world"


@pytest.mark.asyncio
async def test_search_more_like_uses_more_like_id(
    documents: DocumentsClient, load_fixture
) -> None:
    page = {"count": 0, "next": None, "previous": None, "results": []}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/documents/").mock(
            return_value=httpx.Response(200, json=page)
        )
        await documents.search("", more_like=42)
    assert dict(route.calls.last.request.url.params)["more_like_id"] == "42"


@pytest.mark.asyncio
async def test_get_document(documents: DocumentsClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/").mock(
            return_value=httpx.Response(200, json=load_fixture("document_minimal.json"))
        )
        doc = await documents.get(1)
    assert doc.id == 1
    assert doc.title == "Test Document"


@pytest.mark.asyncio
async def test_get_content(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "title": "x",
                    "content": "OCR content here",
                    "created": "2026-04-23T10:00:00Z",
                    "tags": [],
                    "notes": [],
                    "custom_fields": [],
                },
            )
        )
        content = await documents.get_content(1)
    assert content == "OCR content here"


@pytest.mark.asyncio
async def test_get_thumbnail_returns_bytes(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/thumb/").mock(
            return_value=httpx.Response(
                200, content=b"\x89PNGfakebytes", headers={"content-type": "image/png"}
            )
        )
        data, content_type = await documents.get_thumbnail(1)
    assert data.startswith(b"\x89PNG")
    assert content_type == "image/png"


@pytest.mark.asyncio
async def test_get_metadata(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/metadata/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "original_checksum": "abc",
                    "original_size": 12345,
                    "original_mime_type": "application/pdf",
                },
            )
        )
        meta = await documents.get_metadata(1)
    assert meta.original_checksum == "abc"


@pytest.mark.asyncio
async def test_get_notes(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/notes/").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "note": "hi",
                        "created": "2026-04-23T10:00:00Z",
                        "user": 1,
                    }
                ],
            )
        )
        notes = await documents.get_notes(1)
    assert notes[0].note == "hi"


@pytest.mark.asyncio
async def test_get_history(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/history/").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "timestamp": "2026-04-23T10:00:00Z",
                        "action": "modify",
                        "actor": "peter",
                    }
                ],
            )
        )
        hist = await documents.get_history(1)
    assert hist[0].action == "modify"


@pytest.mark.asyncio
async def test_get_suggestions(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/documents/1/suggestions/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "correspondents": [7],
                    "tags": [],
                    "document_types": [],
                    "dates": [],
                },
            )
        )
        s = await documents.get_suggestions(1)
    assert s.correspondents == [7]
