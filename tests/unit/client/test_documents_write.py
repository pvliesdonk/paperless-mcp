"""Tests for DocumentsClient write operations."""

from __future__ import annotations

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
    import json

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
    import json

    body = json.loads(route.calls.last.request.content)
    assert body == {
        "documents": [1, 2, 3],
        "method": "add_tag",
        "parameters": {"tag": 5},
    }


@pytest.mark.asyncio
async def test_add_note(documents: DocumentsClient) -> None:
    returned = {"id": 9, "note": "new", "created": "2026-04-23T10:00:00Z", "user": 1}
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/documents/1/notes/").mock(
            return_value=httpx.Response(200, json=[returned])
        )
        note = await documents.add_note(1, "new")
    assert note.note == "new"
    import json

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
