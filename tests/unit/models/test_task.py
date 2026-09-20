from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

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


def test_v10_fields_and_legacy_projection(load_fixture: Callable[[str], Any]) -> None:
    task = Task.model_validate(load_fixture("task_v10_success.json"))
    assert task.status is TaskStatus.SUCCESS
    assert task.task_type == "consume_file"
    assert task.trigger_source == "api_upload"
    assert task.result_data == {"document_id": 42}
    assert task.related_document_ids == [42]
    assert task.duration_seconds == 3 and task.wait_time_seconds == 2
    assert task.date_started is not None and task.date_started.tzinfo is not None
    assert task.task_file_name == "invoice.pdf"
    assert task.type == "manual_task"
    assert task.result == "Success. New document id 42 created"
    assert task.related_document == "42"
    assert task.model_dump()["task_name"] == "consume_file"


def test_v9_fields_do_not_invent_structured_results(
    load_fixture: Callable[[str], Any],
) -> None:
    task = Task.model_validate(
        {**load_fixture("task_success.json"), "task_name": "check_sanity"}
    )
    assert task.task_type == "sanity_check"
    assert task.input_data == {"filename": "invoice.pdf"}
    assert task.related_document_ids == [42]
    assert task.result_data is None
    assert task.trigger_source is None  # auto_task cannot identify the v10 source


def test_v10_multiple_related_documents_are_preserved(
    load_fixture: Callable[[str], Any],
) -> None:
    payload = load_fixture("task_v10_success.json")
    payload.update(
        related_document_ids=[42, 43], result_data={"document_ids": [42, 43]}
    )
    task = Task.model_validate(payload)
    assert task.related_document_ids == [42, 43]
    assert task.related_document == "42"
    assert task.result is None


def test_task_invalid_inputs_raise_validation_error() -> None:
    import pytest
    from pydantic import ValidationError

    values: list[Any] = [[], {"status": 1}, {"status": "unknown"}]
    for value in values:
        with pytest.raises(ValidationError):
            Task.model_validate(value)


@pytest.mark.parametrize(
    "data,expected",
    [
        (None, None),
        ({}, None),
        ({"reason": "Skipped"}, "Skipped"),
        ({"duplicate_of": 7}, "Not consuming: It is a duplicate of document #7"),
        ({"error_message": "Failed"}, "Failed"),
    ],
)
@pytest.mark.parametrize(
    "trigger,legacy",
    [
        ("system", "auto_task"),
        ("scheduled", "scheduled_task"),
        (None, None),
    ],
)
def test_v10_legacy_results(
    load_fixture: Callable[[str], Any],
    data: dict[str, Any] | None,
    expected: str | None,
    trigger: str | None,
    legacy: str | None,
) -> None:
    payload = load_fixture("task_v10_success.json")
    payload.update(
        result_data=data,
        related_document_ids=[],
        trigger_source=trigger,
        input_data={},
        task_type="llm_index",
    )
    task = Task.model_validate(payload)
    assert task.result == expected
    assert task.type == legacy
    assert task.related_document is None
    assert task.model_dump()["task_name"] == "llmindex_update"


@pytest.mark.parametrize(
    "trigger,legacy",
    [
        ("scheduled", "scheduled_task"),
        ("system", "auto_task"),
        ("email_consume", "auto_task"),
        ("folder_consume", "auto_task"),
        ("web_ui", "manual_task"),
        ("api_upload", "manual_task"),
        ("manual", "manual_task"),
        ("future_trigger", "manual_task"),
    ],
)
def test_v10_trigger_projects_legacy_type(
    load_fixture: Callable[[str], Any], trigger: str, legacy: str
) -> None:
    """Match Paperless 3.1.3 TaskSerializerV9.get_type, including its fallback."""
    payload = load_fixture("task_v10_success.json")
    payload["trigger_source"] = trigger
    task = Task.model_validate(payload)
    assert task.type == legacy
    assert task.trigger_source == trigger
