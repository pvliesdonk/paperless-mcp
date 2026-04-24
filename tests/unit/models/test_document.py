from __future__ import annotations

from paperless_mcp.models.document import (
    CustomFieldInstance,
    Document,
    DocumentHistoryEntry,
    DocumentMetadata,
    DocumentNote,
    DocumentPatch,
    DocumentSuggestions,
)


def test_document_minimal(load_fixture) -> None:
    doc = Document.model_validate(load_fixture("document_minimal.json"))
    assert doc.id == 1
    assert doc.title == "Test Document"
    assert doc.correspondent is None
    assert doc.tags == []


def test_document_full(load_fixture) -> None:
    doc = Document.model_validate(load_fixture("document_full.json"))
    assert doc.id == 42
    assert doc.tags == [1, 4, 9]
    assert doc.notes[0].note == "Paid 2026-04-22"
    assert doc.custom_fields[0].field == 2


def test_document_forward_compatible(load_fixture) -> None:
    doc = Document.model_validate(load_fixture("document_full.json"))
    assert doc.some_future_paperless_field == "that we don't know about yet"  # type: ignore[attr-defined]


def test_document_patch_strict_forbids_extra() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DocumentPatch.model_validate({"nonexistent_field": "x"})


def test_document_patch_allows_partial() -> None:
    patch = DocumentPatch.model_validate({"title": "New title"})
    assert patch.model_dump(exclude_unset=True) == {"title": "New title"}


def test_document_note_roundtrip() -> None:
    note = DocumentNote.model_validate(
        {"id": 5, "note": "hi", "created": "2026-04-23T10:00:00Z", "user": 1}
    )
    assert note.id == 5


def test_document_note_accepts_nested_user_object() -> None:
    """Newer Paperless-NGX returns ``user`` as a nested object, not a bare ID."""
    note = DocumentNote.model_validate(
        {
            "id": 5,
            "note": "hi",
            "created": "2026-04-23T10:00:00Z",
            "user": {
                "id": 3,
                "username": "peter",
                "first_name": "Peter",
                "last_name": "van Liesdonk",
            },
        }
    )
    assert note.user == 3


def test_document_owner_accepts_nested_user_object() -> None:
    """``owner`` likewise: collapses dict input down to the user ID."""
    doc = Document.model_validate(
        {
            "id": 1,
            "title": "x",
            "created": "2026-04-23T10:00:00Z",
            "owner": {"id": 7, "username": "alice"},
        }
    )
    assert doc.owner == 7


def test_document_metadata_accepts_empty() -> None:
    meta = DocumentMetadata.model_validate({})
    assert meta.model_dump(exclude_none=True) == {}


def test_document_history_entry_roundtrip() -> None:
    entry = DocumentHistoryEntry.model_validate(
        {"timestamp": "2026-04-23T10:00:00Z", "action": "modify", "actor": "peter"}
    )
    assert entry.action == "modify"
    assert entry.actor == "peter"


def test_document_history_entry_accepts_nested_actor_object() -> None:
    """Newer Paperless-NGX returns ``actor`` as a nested user object."""
    entry = DocumentHistoryEntry.model_validate(
        {
            "timestamp": "2026-04-23T10:00:00Z",
            "action": "modify",
            "actor": {"id": 3, "username": "peter", "first_name": "Peter"},
        }
    )
    assert entry.actor == "peter"


def test_document_suggestions_accepts_empty_lists() -> None:
    s = DocumentSuggestions.model_validate(
        {"tags": [], "correspondents": [], "document_types": [], "dates": []}
    )
    assert s.tags == []


def test_custom_field_instance_variadic_value() -> None:
    inst = CustomFieldInstance.model_validate({"field": 2, "value": 42})
    assert inst.value == 42
    inst2 = CustomFieldInstance.model_validate({"field": 3, "value": None})
    assert inst2.value is None
