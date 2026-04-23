"""Tests for shared Pydantic models."""
from __future__ import annotations
import pytest
from pydantic import BaseModel, ConfigDict
from paperless_mcp.models.common import (
    BulkEditOperation, BulkEditResult, DownloadLink, Paginated, UploadTaskAcknowledgement,
)

class _Item(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int

def test_paginated_parses_empty() -> None:
    page = Paginated[_Item].model_validate({"count": 0, "next": None, "previous": None, "results": []})
    assert page.count == 0
    assert page.results == []

def test_paginated_parses_results() -> None:
    page = Paginated[_Item].model_validate({"count": 2, "next": "http://x/?page=2", "previous": None, "results": [{"id": 1, "extra": "hi"}, {"id": 2}]})
    assert [r.id for r in page.results] == [1, 2]
    assert page.results[0].extra == "hi"

def test_bulk_edit_operation_enum() -> None:
    assert BulkEditOperation("set_correspondent") == BulkEditOperation.SET_CORRESPONDENT
    with pytest.raises(ValueError):
        BulkEditOperation("nonsense")

def test_bulk_edit_result_parses() -> None:
    result = BulkEditResult.model_validate({"result": "OK"})
    assert result.result == "OK"

def test_download_link_shape() -> None:
    link = DownloadLink(download_url="https://dl.example/abc", expires_in_seconds=300, content_type="application/pdf", filename="invoice.pdf")
    assert link.expires_in_seconds == 300

def test_upload_task_acknowledgement() -> None:
    ack = UploadTaskAcknowledgement.model_validate({"task_id": "abc-123"})
    assert ack.task_id == "abc-123"
