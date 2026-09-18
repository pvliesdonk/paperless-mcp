"""Tool-layer tests for list_tasks pagination."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskType
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    assert kwargs.get("task_type") is None


@pytest.mark.asyncio
async def test_list_tasks_forwards_task_type(mock_client: Any) -> None:
    # The filter that makes bulk_edit_documents' queued rebuild observable.
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    tasks_mod.register(mcp, ctx)
    mock_client.tasks.list.return_value = Paginated[Task].model_validate(
        {"count": 0, "results": []}
    )

    async with Client(mcp) as c:
        await c.call_tool("list_tasks", {"task_type": "bulk_update"})

    kwargs = mock_client.tasks.list.await_args.kwargs
    assert kwargs["task_type"] is TaskType.BULK_UPDATE


def test_list_tasks_exposes_task_type_choices(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    tasks_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    schema = tools["list_tasks"].parameters
    assert "task_type" in schema["properties"]
    # Every upstream task type is offered, not just the one bulk edits queue.
    # The enum is inlined into the property's anyOf, beside the null variant.
    variants = schema["properties"]["task_type"]["anyOf"]
    enum_values = {value for variant in variants for value in variant.get("enum", ())}
    assert enum_values == {member.value for member in TaskType}


@pytest.mark.asyncio
async def test_list_tasks_result_carries_task_name(mock_client: Any) -> None:
    # The kind of work arrives as `task_name` at payload version 9 — an
    # undeclared field kept by `extra="allow"`, which list_tasks' docstring
    # promises reaches the caller.  `type` is the trigger source instead.
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    tasks_mod.register(mcp, ctx)
    mock_client.tasks.list.return_value = Paginated[Task].model_validate(
        {
            "count": 1,
            "results": [
                {
                    "id": 3950,
                    "task_id": "2cf8a2c0",
                    "task_name": "bulk_update",
                    "type": "auto_task",
                    "status": "SUCCESS",
                    "date_created": "2026-09-16T11:54:21.192534+02:00",
                    "acknowledged": False,
                }
            ],
        }
    )

    async with Client(mcp) as c:
        result = await c.call_tool("list_tasks", {"task_type": "bulk_update"})

    assert result.structured_content is not None
    task = result.structured_content["results"][0]
    assert task["task_name"] == "bulk_update"
    assert task["type"] == "auto_task"
