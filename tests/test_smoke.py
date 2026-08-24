"""Smoke tests for Paperless MCP."""

from __future__ import annotations

import pytest

from paperless_mcp.server import make_server


def test_make_server_constructs(monkeypatch: pytest.MonkeyPatch) -> None:
    """make_server() returns a FastMCP instance without raising."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "test-token-smoke")
    server = make_server()
    assert server is not None


@pytest.mark.asyncio
async def test_all_tools_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    """make_server() exposes all expected tools via list_tools()."""
    from fastmcp import Client

    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "test-token-smoke")
    server = make_server()
    async with Client(server) as client:
        tools = await client.list_tools()
    names = {t.name for t in tools}
    # The transfer route (create_download_link) needs HTTP transport and a
    # configured base URL — neither holds for the default stdio path used here.
    assert len(tools) >= 49
    assert "create_download_link" not in names
    for expected in ("list_documents", "create_tag", "wait_for_task", "get_statistics"):
        assert expected in names, f"missing tool: {expected}"


@pytest.mark.asyncio
async def test_download_link_registered_over_http_with_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_download_link is registered over HTTP once base_url is set."""
    from fastmcp import Client

    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "test-token-smoke")
    monkeypatch.setenv("PAPERLESS_MCP_BASE_URL", "https://mcp.example.com")
    server = make_server(transport="http")
    async with Client(server) as client:
        tools = await client.list_tools()
    names = {t.name for t in tools}
    assert "create_download_link" in names
    # No matching write operation for a generic transfer ref in this domain —
    # upload_document already covers document ingestion with real metadata.
    assert "create_upload_link" not in names


@pytest.mark.asyncio
async def test_download_link_absent_over_http_without_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The transfer route is skipped (not a hard failure) without base_url."""
    from fastmcp import Client

    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "test-token-smoke")
    monkeypatch.delenv("PAPERLESS_MCP_BASE_URL", raising=False)
    server = make_server(transport="http")
    async with Client(server) as client:
        tools = await client.list_tools()
    names = {t.name for t in tools}
    assert "create_download_link" not in names
