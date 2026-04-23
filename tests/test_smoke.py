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
