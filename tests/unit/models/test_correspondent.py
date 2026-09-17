from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from paperless_mcp.models.correspondent import (
    Correspondent,
    CorrespondentCreate,
    CorrespondentPatch,
)


def test_correspondent_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    c = Correspondent.model_validate(load_fixture("correspondent.json"))
    assert c.id == 1
    assert c.name == "ACME Corporation"
    assert c.document_count == 12


def test_correspondent_last_correspondence_naive_gets_utc() -> None:
    """A naive ``last_correspondence`` should keep an explicit offset once parsed."""
    c = Correspondent.model_validate(
        {"id": 2, "name": "Naive Corp", "last_correspondence": "2026-04-20T14:30:00"}
    )
    assert c.last_correspondence is not None
    assert c.last_correspondence.tzinfo is not None


def test_correspondent_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        CorrespondentCreate.model_validate({})


def test_correspondent_patch_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        CorrespondentPatch.model_validate({"unknown": 1})
