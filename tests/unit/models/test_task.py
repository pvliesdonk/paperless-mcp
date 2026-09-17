from __future__ import annotations

from collections.abc import Callable
from typing import Any

from paperless_mcp.models.task import Task, TaskStatus


def test_task_success_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    t = Task.model_validate(load_fixture("task_success.json"))
    assert t.task_id == "abc-123-success"
    assert t.status is TaskStatus.SUCCESS
    assert t.related_document == "42"


def test_task_pending_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    t = Task.model_validate(load_fixture("task_pending.json"))
    assert t.status is TaskStatus.PENDING
    assert t.date_done is None


def test_task_related_document_int_coerced_to_str() -> None:
    """Paperless-NGX may return ``related_document`` as an integer ID."""
    t = Task.model_validate(
        {
            "id": 101,
            "task_id": "int-related-doc",
            "date_created": "2026-04-23T10:00:00Z",
            "status": "SUCCESS",
            "related_document": 42,
        }
    )
    assert t.related_document == "42"


def test_task_date_created_naive_gets_utc() -> None:
    """A naive ``date_created`` should keep an explicit offset once parsed."""
    t = Task.model_validate(
        {
            "id": 102,
            "task_id": "naive-date",
            "date_created": "2026-04-23T10:00:00",
            "status": "PENDING",
        }
    )
    assert t.date_created.tzinfo is not None


def test_task_status_values() -> None:
    assert {s.value for s in TaskStatus} >= {
        "PENDING",
        "STARTED",
        "SUCCESS",
        "FAILURE",
        "RETRY",
        "REVOKED",
    }
