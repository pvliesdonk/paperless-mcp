"""Tests for shared Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict

from paperless_mcp.models.common import (
    BulkEditOperation,
    BulkEditResult,
    DownloadLink,
    Paginated,
    UploadTaskAcknowledgement,
)


class _Item(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int


def test_paginated_parses_empty() -> None:
    page = Paginated[_Item].model_validate(
        {"count": 0, "next": None, "previous": None, "results": []}
    )
    assert page.count == 0
    assert page.results == []


def test_paginated_parses_results() -> None:
    page = Paginated[_Item].model_validate(
        {
            "count": 2,
            "next": "http://x/?page=2",
            "previous": None,
            "results": [{"id": 1, "extra": "hi"}, {"id": 2}],
        }
    )
    assert [r.id for r in page.results] == [1, 2]
    assert page.results[0].extra == "hi"  # type: ignore[attr-defined]
    # The ``next`` URL is normalised to a bare ``page=N`` marker by the
    # Paginated validator; assert it here so the fixture shape doesn't
    # silently drift from the normalised output shape.
    assert page.next == "page=2"


def test_paginated_normalises_full_url_next_to_page_marker() -> None:
    page = Paginated[_Item].model_validate(
        {
            "count": 3,
            "next": "http://paperless-ngx:8000/api/documents/?page=2",
            "previous": None,
            "results": [{"id": 1}],
        }
    )
    assert page.next == "page=2"
    assert page.previous is None


def test_paginated_normalises_previous_url() -> None:
    page = Paginated[_Item].model_validate(
        {
            "count": 3,
            "next": None,
            "previous": "http://paperless-ngx:8000/api/documents/?page=1&tag=4",
            "results": [{"id": 3}],
        }
    )
    assert page.previous == "page=1"


def test_paginated_passthrough_bare_page_marker() -> None:
    # Client-paginated endpoints (tasks) already emit "page=N"; the validator
    # must leave that shape unchanged.
    page = Paginated[_Item].model_validate(
        {"count": 1, "next": "page=2", "previous": None, "results": [{"id": 1}]}
    )
    assert page.next == "page=2"


def test_paginated_next_without_page_param_becomes_none(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level("WARNING", logger="paperless_mcp.models.common"):
        page = Paginated[_Item].model_validate(
            {
                "count": 1,
                "next": "http://paperless-ngx:8000/api/documents/",
                "previous": None,
                "results": [{"id": 1}],
            }
        )
    assert page.next is None
    # Surfacing unexpected pagination shapes at WARNING helps operators
    # diagnose silently-truncated walks in production.
    assert any(
        "normalise_page_marker unexpected_shape" in rec.message
        for rec in caplog.records
    )


def test_paginated_next_none_stays_none() -> None:
    page = Paginated[_Item].model_validate(
        {"count": 1, "next": None, "previous": None, "results": [{"id": 1}]}
    )
    assert page.next is None
    assert page.previous is None


def test_paginated_drops_all_ids_from_upstream() -> None:
    page = Paginated[_Item].model_validate(
        {
            "count": 3,
            "next": None,
            "previous": None,
            "all": [1, 2, 3, 4, 5],
            "results": [{"id": 1}, {"id": 2}, {"id": 3}],
        }
    )
    dumped = page.model_dump()
    assert "all" not in dumped
    assert "all_ids" not in dumped
    assert not hasattr(page, "all_ids")
    assert page.count == 3
    assert [r.id for r in page.results] == [1, 2, 3]


def test_bulk_edit_operation_enum() -> None:
    assert BulkEditOperation("set_correspondent") == BulkEditOperation.SET_CORRESPONDENT
    with pytest.raises(ValueError):
        BulkEditOperation("nonsense")


def test_bulk_edit_result_parses() -> None:
    result = BulkEditResult.model_validate({"result": "OK"})
    assert result.result == "OK"


def test_download_link_shape() -> None:
    link = DownloadLink(
        download_url="https://dl.example/abc",
        expires_in_seconds=300,
        content_type="application/pdf",
        filename="invoice.pdf",
    )
    assert link.expires_in_seconds == 300


def test_upload_task_acknowledgement() -> None:
    ack = UploadTaskAcknowledgement.model_validate({"task_id": "abc-123"})
    assert ack.task_id == "abc-123"
