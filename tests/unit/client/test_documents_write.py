"""Tests for DocumentsClient write operations."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.documents import DocumentsClient
from paperless_mcp.models.common import BulkEditOperation
from paperless_mcp.models.document import DocumentPatch


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
async def test_update_sends_only_set_fields(
    documents: DocumentsClient, load_fixture
) -> None:
    updated = load_fixture("document_minimal.json")
    updated["title"] = "Renamed"
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.patch("/api/documents/1/").mock(
            return_value=httpx.Response(200, json=updated)
        )
        doc = await documents.update(1, DocumentPatch(title="Renamed"))
    assert doc.title == "Renamed"
    # only set fields should be in the payload
    payload = route.calls.last.request.content
    assert json.loads(payload) == {"title": "Renamed"}


@pytest.mark.asyncio
async def test_delete(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/documents/1/").mock(return_value=httpx.Response(204))
        await documents.delete(1)
    assert route.called


@pytest.mark.asyncio
async def test_upload_sends_multipart(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/documents/post_document/").mock(
            return_value=httpx.Response(200, json="abc-task-uuid")
        )
        ack = await documents.upload(
            filename="invoice.pdf",
            content=b"%PDF-1.4\n...",
            title="Invoice",
            tags=[1, 2],
            correspondent=7,
        )
    assert ack.task_id == "abc-task-uuid"
    request = route.calls.last.request
    assert b'filename="invoice.pdf"' in request.content
    # multipart boundary should carry extra fields
    assert b'name="title"' in request.content
    assert b'name="tags"' in request.content


@pytest.mark.asyncio
async def test_bulk_edit(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/documents/bulk_edit/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        result = await documents.bulk_edit(
            document_ids=[1, 2, 3],
            method=BulkEditOperation.ADD_TAG,
            parameters={"tag": 5},
        )
    assert result.result == "OK"
    body = json.loads(route.calls.last.request.content)
    assert body == {
        "documents": [1, 2, 3],
        "method": "add_tag",
        "parameters": {"tag": 5},
    }


@pytest.mark.asyncio
async def test_add_note(documents: DocumentsClient) -> None:
    existing = {"id": 1, "note": "old", "created": "2026-04-01T10:00:00Z", "user": 1}
    newest = {"id": 9, "note": "new", "created": "2026-04-23T10:00:00Z", "user": 1}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/documents/1/notes/").mock(
            return_value=httpx.Response(200, json=[existing, newest])
        )
        note = await documents.add_note(1, "new")
    # add_note returns the last item in the list (newest note, not the first)
    assert note.id == 9
    assert note.note == "new"
    body = json.loads(route.calls.last.request.content)
    assert body == {"note": "new"}


@pytest.mark.asyncio
async def test_delete_note(documents: DocumentsClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.delete("/api/documents/1/notes/").mock(
            return_value=httpx.Response(204)
        )
        await documents.delete_note(1, 9)
    assert "id=9" in str(route.calls.last.request.url)


@pytest.mark.asyncio
async def test_delete_note_404_raises_paperless_api_error(
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    from paperless_mcp.client import PaperlessClient
    from paperless_mcp.client._errors import PaperlessAPIError

    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.delete("/api/documents/42/notes/").mock(
            return_value=httpx.Response(
                404, json={"detail": "No Note matches the given query."}
            )
        )
        c = PaperlessClient(base_url=paperless_base_url, api_token=paperless_api_token)
        try:
            with pytest.raises(PaperlessAPIError) as exc_info:
                await c.documents.delete_note(42, 99)
        finally:
            await c.aclose()
    assert exc_info.value.status_code == 404
