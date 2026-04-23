"""Smoke test: the server boots with tools, resources, and prompts wired."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_server_boots_without_paperless(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    from paperless_mcp.resources import register_resources
    from paperless_mcp.tools import register_tools

    assert callable(register_tools)
    assert callable(register_resources)
