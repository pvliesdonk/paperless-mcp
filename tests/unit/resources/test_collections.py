from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from paperless_mcp.resources import collections as collections_mod
from paperless_mcp.tools._context import ToolContext


async def _empty_paginate(*_args: Any, **_kwargs: Any) -> AsyncGenerator[Any, None]:
    return
    yield  # pragma: no cover


def _mock_client() -> Any:
    client = MagicMock()
    client.http.paginate = _empty_paginate
    client.system.statistics = AsyncMock(
        return_value=MagicMock(
            model_dump_json=MagicMock(return_value='{"documents_total": 0}')
        )
    )
    client.system.remote_version = AsyncMock(
        return_value=MagicMock(
            model_dump_json=MagicMock(return_value='{"version": "2.7.2"}')
        )
    )
    return client


def _uris(mcp: FastMCP) -> set[str]:
    return {str(r.uri) for r in asyncio.run(mcp.list_resources())}


def test_all_collection_uris_registered() -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=_mock_client(), read_only=False, default_page_size=25, public_url=""
    )
    collections_mod.register(mcp, ctx)
    uris = _uris(mcp)
    assert "config://paperless" in uris
    assert "stats://paperless" in uris
    assert "remote-version://paperless" in uris
    assert "tags://paperless" in uris
    assert "correspondents://paperless" in uris
    assert "document-types://paperless" in uris
    assert "custom-fields://paperless" in uris
    assert "storage-paths://paperless" in uris
    assert "saved-views://paperless" in uris


@pytest.mark.asyncio
async def test_tags_resource_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """tags://paperless returns a non-empty JSON response."""
    from fastmcp import Client

    mcp = FastMCP("test")
    ctx = ToolContext(
        client=_mock_client(), read_only=False, default_page_size=25, public_url=""
    )
    collections_mod.register(mcp, ctx)
    async with Client(mcp) as client:
        result = await client.read_resource("tags://paperless")
    assert result  # non-empty response
