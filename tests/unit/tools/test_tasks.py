"""Tool-layer tests for list_tasks pagination."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task
from paperless_mcp.tools import tasks as tasks_mod
from paperless_mcp.tools._context import ToolContext


@pytest.fixture
def mock_client() -> Any:
    client = MagicMock()
    client.tasks.list = AsyncMock()
    client.tasks.get = AsyncMock()
    client.tasks.wait_for = AsyncMock()
    return client


def test_list_tasks_registered_with_pagination(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
    tasks_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    assert "list_tasks" in tools
    schema = tools["list_tasks"].parameters
    assert "page" in schema["properties"]
    assert "page_size" in schema["properties"]
    assert "include_acknowledged" in schema["properties"]


@pytest.mark.asyncio
async def test_list_tasks_default_forwards_filter(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
    tasks_mod.register(mcp, ctx)
    mock_client.tasks.list.return_value = Paginated[Task].model_validate(
        {"count": 0, "results": []}
    )

    async with Client(mcp) as c:
        await c.call_tool("list_tasks", {})

    mock_client.tasks.list.assert_awaited_once()
    kwargs = mock_client.tasks.list.await_args.kwargs
    assert kwargs["page"] == 1
    assert kwargs["page_size"] == 25
    assert kwargs.get("include_acknowledged") is False
    assert kwargs.get("acknowledged") is None
