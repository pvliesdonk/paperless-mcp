"""Shared test fixtures for Paperless MCP."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from fastmcp import Client

from paperless_mcp.server import make_server


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip all ``PAPERLESS_MCP_*`` env vars before each test."""
    for key in list(os.environ):
        if key.startswith("PAPERLESS_MCP_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
async def client() -> AsyncIterator[Client]:
    """Return an in-memory FastMCP client connected to a fresh server."""
    server = make_server()
    async with Client(server) as c:
        yield c
