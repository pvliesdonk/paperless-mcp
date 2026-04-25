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
    for expected in ("list_documents", "create_tag", "wait_for_task", "get_statistics"):
        assert expected in names, f"missing tool: {expected}"
