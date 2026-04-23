from __future__ import annotations

import pytest
from pydantic import ValidationError

from paperless_mcp.models.tag import Tag, TagCreate, TagPatch


def test_tag_roundtrip(load_fixture) -> None:
    tag = Tag.model_validate(load_fixture("tag.json"))
    assert tag.id == 1
    assert tag.name == "Invoice"
    assert tag.document_count == 42


def test_tag_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        TagCreate.model_validate({})


def test_tag_create_minimal() -> None:
    body = TagCreate(name="New Tag")
    assert body.model_dump(exclude_unset=True) == {"name": "New Tag"}


def test_tag_patch_partial() -> None:
    patch = TagPatch(name="Renamed")
    assert patch.model_dump(exclude_unset=True) == {"name": "Renamed"}


def test_tag_patch_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        TagPatch.model_validate({"not_a_field": 1})
