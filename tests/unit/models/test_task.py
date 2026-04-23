from __future__ import annotations
from paperless_mcp.models.task import Task, TaskStatus

def test_task_success_roundtrip(load_fixture) -> None:
    t = Task.model_validate(load_fixture("task_success.json"))
    assert t.task_id == "abc-123-success"
    assert t.status is TaskStatus.SUCCESS
    assert t.related_document == "42"

def test_task_pending_roundtrip(load_fixture) -> None:
    t = Task.model_validate(load_fixture("task_pending.json"))
    assert t.status is TaskStatus.PENDING
    assert t.date_done is None

def test_task_status_values() -> None:
    assert {s.value for s in TaskStatus} >= {"PENDING", "STARTED", "SUCCESS", "FAILURE", "RETRY", "REVOKED"}
