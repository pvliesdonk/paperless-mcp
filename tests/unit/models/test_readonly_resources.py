from __future__ import annotations

from collections.abc import Callable
from typing import Any

from paperless_mcp.models.saved_view import SavedView
from paperless_mcp.models.share_link import ShareLink, ShareLinkFileVersion
from paperless_mcp.models.storage_path import StoragePath


def test_storage_path_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    sp = StoragePath.model_validate(load_fixture("storage_path.json"))
    assert sp.id == 2
    assert sp.path == "Invoices/{created_year}/"
    assert sp.document_count == 120


def test_saved_view_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    sv = SavedView.model_validate(load_fixture("saved_view.json"))
    assert sv.id == 1
    assert sv.filter_rules[0]["rule_type"] == 29


def test_share_link_roundtrip(load_fixture: Callable[[str], Any]) -> None:
    sl = ShareLink.model_validate(load_fixture("share_link.json"))
    assert sl.id == 5
    assert sl.file_version is ShareLinkFileVersion.ARCHIVE
