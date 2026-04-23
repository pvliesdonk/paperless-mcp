"""Tests for the tool registry helper."""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from paperless_mcp.tools._registry import load_svg_data_uri


def test_load_svg_data_uri(tmp_path: Path) -> None:
    svg_file = tmp_path / "foo.svg"
    svg_file.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
    uri = load_svg_data_uri(svg_file)
    assert uri.startswith("data:image/svg+xml;base64,")
    payload = uri.split(",", 1)[1]
    assert base64.b64decode(payload).startswith(b"<svg")


def test_load_svg_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_svg_data_uri(tmp_path / "nope.svg")
