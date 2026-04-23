"""Registration tests for observability tool modules."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from paperless_mcp.tools import (
    saved_views as saved_views_mod,
    share_links as share_links_mod,
    storage_paths as storage_paths_mod,
    system as system_mod,
    tasks as tasks_mod,
)
from paperless_mcp.tools._context import ToolContext


def _mock_client() -> Any:
    client = MagicMock()
    for attr in ("storage_paths", "saved_views", "share_links"):
        sub = getattr(client, attr)
        for meth in ("list", "get"):
            setattr(sub, meth, AsyncMock())
    client.tasks.list = AsyncMock()
    client.tasks.get = AsyncMock()
    client.tasks.wait_for = AsyncMock()
    client.system.statistics = AsyncMock()
    client.system.remote_version = AsyncMock()
    return client


def _names(mcp: FastMCP) -> set[str]:
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


@pytest.mark.parametrize(
    "module, expected",
    [
        (storage_paths_mod, {"list_storage_paths", "get_storage_path"}),
        (saved_views_mod, {"list_saved_views", "get_saved_view"}),
        (share_links_mod, {"list_share_links", "get_share_link"}),
        (tasks_mod, {"list_tasks", "get_task", "wait_for_task"}),
        (system_mod, {"get_statistics", "get_remote_version"}),
    ],
)
def test_observability_tools_register(module: Any, expected: set[str]) -> None:
    for read_only in (True, False):
        mcp = FastMCP("test")
        ctx = ToolContext(client=_mock_client(), read_only=read_only, default_page_size=25)
        module.register(mcp, ctx)
        assert expected.issubset(_names(mcp))
