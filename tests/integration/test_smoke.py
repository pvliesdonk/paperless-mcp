"""End-to-end smoke test against a live Paperless-NGX instance."""

from __future__ import annotations

import uuid

import pytest

from paperless_mcp.client import PaperlessClient
from paperless_mcp.models.common import BulkEditOperation
from paperless_mcp.models.document import DocumentPatch
from paperless_mcp.models.tag import TagCreate
from paperless_mcp.models.task import TaskStatus

pytestmark = pytest.mark.integration


async def test_end_to_end(live_client: PaperlessClient) -> None:
    unique = uuid.uuid4().hex[:8]

    tag = await live_client.tags.create(TagCreate(name=f"it-smoke-{unique}"))
    document_id: int | None = None
    try:
        pdf_bytes = (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 72 72]/Resources<<>>>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000053 00000 n \n0000000094 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n150\n%%EOF\n"
        )

        ack = await live_client.documents.upload(
            filename=f"it-smoke-{unique}.pdf",
            content=pdf_bytes,
            title=f"IT smoke {unique}",
            tags=[tag.id],
        )
        task = await live_client.tasks.wait_for(ack.task_id, timeout_seconds=60)
        assert task.status == TaskStatus.SUCCESS, f"task failed: {task.result}"
        assert task.related_document is not None
        document_id = int(task.related_document)

        doc = await live_client.documents.get(document_id)
        assert doc.title == f"IT smoke {unique}"
        assert tag.id in doc.tags

        patched = await live_client.documents.update(
            document_id, DocumentPatch(title=f"IT smoke {unique} (renamed)")
        )
        assert patched.title == f"IT smoke {unique} (renamed)"

        result = await live_client.documents.bulk_edit(
            document_ids=[document_id],
            method=BulkEditOperation.REMOVE_TAG,
            parameters={"tag": tag.id},
        )
        assert result.result == "OK"
    finally:
        if document_id is not None:
            await live_client.documents.delete(document_id)
        await live_client.tags.delete(tag.id)
