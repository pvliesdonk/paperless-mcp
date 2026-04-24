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


@pytest.mark.asyncio
async def test_wrap_catches_httpx_status_error() -> None:
    import httpx

    from paperless_mcp.tools._registry import _wrap_with_error_handling

    async def boom() -> object:
        request = httpx.Request("DELETE", "http://paperless.test/api/x/")
        response = httpx.Response(404, request=request)
        raise httpx.HTTPStatusError("404", request=request, response=response)

    wrapped = _wrap_with_error_handling("delete_document_note", boom)
    result = await wrapped()
    assert isinstance(result, str)
    assert "Error occurred during tool execution" not in result
    assert "404" in result or "not found" in result.lower()


@pytest.mark.asyncio
async def test_wrap_catches_pydantic_validation_error() -> None:
    from pydantic import BaseModel

    from paperless_mcp.tools._registry import _wrap_with_error_handling

    class M(BaseModel):
        n: int

    async def boom() -> object:
        M.model_validate({"n": "not-an-int"})
        return None

    wrapped = _wrap_with_error_handling("delete_document_note", boom)
    result = await wrapped()
    assert isinstance(result, str)
    assert "Error occurred during tool execution" not in result
    assert "validation" in result.lower()
    assert "int" in result.lower()
