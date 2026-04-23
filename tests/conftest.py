"""Shared pytest fixtures for paperless-mcp."""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

import pytest
from fastmcp import Client

from paperless_mcp.server import make_server

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "paperless"


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


@pytest.fixture
def load_fixture() -> Callable[[str], Any]:
    """Load a JSON fixture from tests/fixtures/paperless/."""

    def _load(name: str) -> Any:
        path = FIXTURES_DIR / name
        return json.loads(path.read_text(encoding="utf-8"))

    return _load


@pytest.fixture
def paperless_base_url() -> str:
    return "http://paperless.test"


@pytest.fixture
def paperless_api_token() -> str:
    return "test-token-do-not-use-in-prod"
