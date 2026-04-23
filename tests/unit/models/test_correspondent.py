from __future__ import annotations

import pytest
from pydantic import ValidationError

from paperless_mcp.models.correspondent import (
    Correspondent,
    CorrespondentCreate,
    CorrespondentPatch,
)


def test_correspondent_roundtrip(load_fixture) -> None:
    c = Correspondent.model_validate(load_fixture("correspondent.json"))
    assert c.id == 1
    assert c.name == "ACME Corporation"
    assert c.document_count == 12


def test_correspondent_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        CorrespondentCreate.model_validate({})


def test_correspondent_patch_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        CorrespondentPatch.model_validate({"unknown": 1})
