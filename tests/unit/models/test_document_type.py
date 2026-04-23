from __future__ import annotations
import pytest
from pydantic import ValidationError
from paperless_mcp.models.document_type import DocumentType, DocumentTypeCreate, DocumentTypePatch

def test_document_type_roundtrip(load_fixture) -> None:
    dt = DocumentType.model_validate(load_fixture("document_type.json"))
    assert dt.id == 3
    assert dt.name == "Invoice"

def test_document_type_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        DocumentTypeCreate.model_validate({})

def test_document_type_patch_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        DocumentTypePatch.model_validate({"unknown": 1})
