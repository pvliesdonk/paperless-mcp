"""Smoke test: the server boots with tools, resources, and prompts wired."""

from __future__ import annotations

import pytest
from fastmcp_pvl_core import build_event_store

from paperless_mcp.config import ProjectConfig
from paperless_mcp.server import make_server


def test_server_boots_without_paperless(monkeypatch: pytest.MonkeyPatch) -> None:
    """make_server() registers tools and resources without hitting Paperless."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    server = make_server()
    assert server is not None


def test_http_server_boots_with_kv_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP app construction uses the configured KV-backed event store."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    monkeypatch.setenv("PAPERLESS_MCP_KV_STORE_URL", "memory://")
    config = ProjectConfig.from_env()
    server = make_server(transport="http", config=config)

    app = server.http_app(
        path="/mcp", event_store=build_event_store("PAPERLESS_MCP", config.server)
    )

    assert app is not None
