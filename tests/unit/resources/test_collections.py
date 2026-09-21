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
    ctx = ToolContext(client=_mock_client(), default_page_size=25, public_url="")
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


def test_remote_version_resource_description_names_the_upstream_release() -> None:
    """The resource answers "is there a newer release", not "which instance".

    Its description is the only thing a model reads before choosing between this
    URI and ``get_server_info``, and the URI itself reads like an identity
    lookup.  See ``docs/design/reference/paperless-version-endpoints.md``.
    """
    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), default_page_size=25, public_url="")
    collections_mod.register(mcp, ctx)
    resources = {str(r.uri): r for r in asyncio.run(mcp.list_resources())}
    # Collapse wrapping: the description is a reflowed docstring, so a phrase
    # may straddle a newline and must still count as present.
    raw = resources["remote-version://paperless"].description or ""
    desc = " ".join(raw.lower().split())
    assert "newest release" in desc, desc
    assert "not the version installed" in desc, desc


@pytest.mark.asyncio
async def test_tags_resource_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """tags://paperless returns a non-empty JSON response."""
    from fastmcp import Client

    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), default_page_size=25, public_url="")
    collections_mod.register(mcp, ctx)
    async with Client(mcp) as client:
        result = await client.read_resource("tags://paperless")
    assert result  # non-empty response


@pytest.mark.asyncio
async def test_correspondents_resource_asks_for_last_correspondence() -> None:
    """The resource walks the endpoint itself, so it must ask too (#172).

    Paperless leaves ``last_correspondence`` out of list rows unless the query
    string carries the parameter; ``correspondents://paperless`` would
    otherwise disagree with ``get_correspondent`` and ``list_correspondents``.
    """
    from fastmcp import Client

    seen: dict[str, Any] = {}

    async def paginate(
        path: str, *, params: dict[str, Any] | None = None, **_kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        seen[path] = params
        return
        yield  # pragma: no cover

    client_mock = _mock_client()
    client_mock.http.paginate = paginate
    mcp = FastMCP("test")
    ctx = ToolContext(client=client_mock, default_page_size=25, public_url="")
    collections_mod.register(mcp, ctx)
    async with Client(mcp) as client:
        await client.read_resource("correspondents://paperless")
    assert seen["/api/correspondents/"] == {"last_correspondence": "true"}
