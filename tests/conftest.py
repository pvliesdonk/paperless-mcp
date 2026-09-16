"""Shared test fixtures for Paperless MCP."""

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

# `make_server()` fails fast without these two, and the template-owned tests
# (`test_smoke.py`, `test_task_backend.py`, `test_health.py`) construct a server
# with no env of their own, so they are preset for the whole suite rather than
# in each test. The token is a literal the suite feeds to a mocked transport,
# never a credential.
REQUIRED_ENV = {
    "PAPERLESS_MCP_PAPERLESS_URL": "http://paperless.test",
    "PAPERLESS_MCP_API_TOKEN": "test-token-do-not-use-in-prod",
}


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip all ``PAPERLESS_MCP_*`` env vars, then preset the required pair."""
    for key in list(os.environ):
        if key.startswith("PAPERLESS_MCP_"):
            monkeypatch.delenv(key, raising=False)
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def config_contract_env() -> dict[str, str]:
    """Env vars the template's `test_config_contract.py` presets before it
    constructs the config via an otherwise env-less ``ProjectConfig.from_env()``.

    A domain whose ``from_env`` hard-requires a variable (a fail-fast startup
    contract) should return it here, for example::

        return {"PAPERLESS_MCP_SOURCE_DIR": "/tmp/vault"}
    """
    return dict(REQUIRED_ENV)


@pytest.fixture
async def client() -> AsyncIterator[Client[Any]]:
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
    return REQUIRED_ENV["PAPERLESS_MCP_PAPERLESS_URL"]


@pytest.fixture
def paperless_api_token() -> str:
    return REQUIRED_ENV["PAPERLESS_MCP_API_TOKEN"]
