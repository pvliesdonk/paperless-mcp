"""Preserve released task fields while exposing payload version 10 data.

Mappings follow TaskSerializerV9 in Paperless 3.1.3; see
docs/design/reference/paperless-api-versioning.md.
"""

from __future__ import annotations

from typing import Any

_TASK_NAMES = {"sanity_check": "check_sanity", "llm_index": "llmindex_update"}
_TRIGGER_TYPES = {
    "scheduled": "scheduled_task",
    "system": "auto_task",
    "email_consume": "auto_task",
    "folder_consume": "auto_task",
}


def _legacy_result(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    if data.get("document_id"):
        return f"Success. New document id {data['document_id']} created"
    if data.get("reason"):
        return str(data["reason"])
    if data.get("duplicate_of"):
        return f"Not consuming: It is a duplicate of document #{data['duplicate_of']}"
    return str(data["error_message"]) if data.get("error_message") else None


def _modern_fields(data: dict[str, Any]) -> None:
    old_name = data.get("task_name")
    modern_names = {old: new for new, old in _TASK_NAMES.items()}
    data.setdefault("task_type", modern_names.get(old_name or "", old_name))
    if data.get("task_file_name") is not None:
        data.setdefault("input_data", {"filename": data["task_file_name"]})
    related = data.get("related_document")
    if related is not None and str(related).isdigit():
        data.setdefault("related_document_ids", [int(related)])


def normalize_task_payload(value: Any) -> Any:
    """Expose v10 data and retain v9 compatibility fields without losing values.

    Args:
        value: Task input supplied to Pydantic.

    Returns:
        A copied task mapping with compatibility fields, or the original input
        for Pydantic to reject when it is not a mapping.
    """
    if not isinstance(value, dict):
        return value
    data = dict(value)
    if "task_type" not in data:
        _modern_fields(data)
        return data
    kind = data["task_type"]
    data.setdefault("task_name", _TASK_NAMES.get(kind, kind))
    trigger = data.get("trigger_source")
    if trigger is not None:
        data.setdefault("type", _TRIGGER_TYPES.get(trigger, "manual_task"))
    data.setdefault("task_file_name", (data.get("input_data") or {}).get("filename"))
    data.setdefault("result", _legacy_result(data.get("result_data")))
    ids = data.get("related_document_ids") or []
    data.setdefault("related_document", ids[0] if ids else None)
    return data
