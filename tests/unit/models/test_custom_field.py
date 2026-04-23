from __future__ import annotations

import pytest
from pydantic import ValidationError

from paperless_mcp.models.custom_field import (
    CustomField,
    CustomFieldCreate,
    CustomFieldDataType,
    CustomFieldPatch,
)


def test_custom_field_roundtrip(load_fixture) -> None:
    cf = CustomField.model_validate(load_fixture("custom_field.json"))
    assert cf.id == 2
    assert cf.data_type is CustomFieldDataType.LONGTEXT


def test_custom_field_data_type_enum() -> None:
    assert CustomFieldDataType("string") is CustomFieldDataType.STRING
    with pytest.raises(ValueError):
        CustomFieldDataType("nope")


def test_custom_field_create_requires_fields() -> None:
    with pytest.raises(ValidationError):
        CustomFieldCreate.model_validate({"name": "x"})


def test_custom_field_patch_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        CustomFieldPatch.model_validate({"unknown": 1})
