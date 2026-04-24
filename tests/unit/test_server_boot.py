"""Smoke test: the server boots with tools, resources, and prompts wired."""

from __future__ import annotations

import pytest

from paperless_mcp.server import make_server


@pytest.mark.asyncio
async def test_server_boots_without_paperless(monkeypatch: pytest.MonkeyPatch) -> None:
    """make_server() registers tools and resources without hitting Paperless."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    server = make_server()
    assert server is not None
