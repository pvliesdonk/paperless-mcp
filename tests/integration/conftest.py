"""Fixtures for live Paperless integration tests.

Skipped unless both ``PAPERLESS_MCP_IT_URL`` and ``PAPERLESS_MCP_IT_TOKEN`` are
set.  CI wires these to a disposable paperless-ngx container; locally, point
them at a scratch instance.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest

from paperless_mcp.client import PaperlessClient


def _env_or_skip(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"integration test requires ${name}")
    return value


@pytest.fixture
async def live_client() -> AsyncGenerator[PaperlessClient, None]:
    url = _env_or_skip("PAPERLESS_MCP_IT_URL")
    token = _env_or_skip("PAPERLESS_MCP_IT_TOKEN")
    client = PaperlessClient(base_url=url, api_token=token)
    try:
        yield client
    finally:
        await client.aclose()
