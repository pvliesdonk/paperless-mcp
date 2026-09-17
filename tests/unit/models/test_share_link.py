from __future__ import annotations

from collections.abc import Callable
from typing import Any

from paperless_mcp.models.share_link import ShareLink


def test_share_link_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    link = ShareLink.model_validate(load_fixture("share_link.json"))
    assert link.id == 5
    assert link.document == 42


def test_share_link_created_naive_gets_utc() -> None:
    """A naive ``created`` should keep an explicit offset once parsed."""
    link = ShareLink.model_validate(
        {
            "id": 6,
            "created": "2026-01-01T00:00:00",
            "slug": "xyz789",
            "document": 43,
            "file_version": "original",
        }
    )
    assert link.created.tzinfo is not None
