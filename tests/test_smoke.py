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
    assert len(tools) >= 49
    assert "create_download_link" not in names
    for expected in ("list_documents", "create_tag", "wait_for_task", "get_statistics"):
        assert expected in names, f"missing tool: {expected}"


@pytest.mark.asyncio
async def test_tool_allowlist_hides_unlisted_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operator tool visibility limits both listings and invocation surfaces."""
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "test-token-smoke")
    monkeypatch.setenv("PAPERLESS_MCP_TOOLS_ALLOW", "list_documents")
    server = make_server()
    async with Client(server) as client:
        tools = await client.list_tools()
        with pytest.raises(ToolError, match=r"Unknown tool: 'create_tag'"):
            await client.call_tool("create_tag", {})

    assert {tool.name for tool in tools} == {"list_documents"}
