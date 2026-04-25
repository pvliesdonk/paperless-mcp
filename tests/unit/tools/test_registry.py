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
async def test_wrap_raises_tool_error_on_paperless_api_error() -> None:
    from fastmcp.exceptions import ToolError

    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._registry import _wrap_with_error_handling

    async def boom() -> object:
        raise NotFoundError(404, "No Tag matches the given query.")

    wrapped = _wrap_with_error_handling("get_tag", boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Paperless API error 404:")
    assert "No Tag matches" in str(excinfo.value)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_httpx_status_error() -> None:
    import httpx
    from fastmcp.exceptions import ToolError

    from paperless_mcp.tools._registry import _wrap_with_error_handling

    async def boom() -> object:
        request = httpx.Request("DELETE", "http://paperless.test/api/x/")
        response = httpx.Response(404, json={"detail": "Not found."}, request=request)
        raise httpx.HTTPStatusError("404", request=request, response=response)

    wrapped = _wrap_with_error_handling("delete_document_note", boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Paperless API error 404:")
    assert "Not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_request_error() -> None:
    import httpx
    from fastmcp.exceptions import ToolError

    from paperless_mcp.tools._registry import _wrap_with_error_handling

    async def boom() -> object:
        raise httpx.ConnectError("name resolution failed")

    wrapped = _wrap_with_error_handling("get_tag", boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert "Network error connecting to Paperless" in str(excinfo.value)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_pydantic_validation_error() -> None:
    from fastmcp.exceptions import ToolError
    from pydantic import BaseModel

    from paperless_mcp.tools._registry import _wrap_with_error_handling

    class M(BaseModel):
        n: int

    async def boom() -> object:
        M.model_validate({"n": "not-an-int"})
        return None

    wrapped = _wrap_with_error_handling("delete_document_note", boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Response validation failed (1 error(s)):")
