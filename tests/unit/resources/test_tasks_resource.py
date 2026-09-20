from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP
from mcp.types import TextResourceContents

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task
from paperless_mcp.resources import tasks as tasks_mod
from paperless_mcp.tools._context import ToolContext


@pytest.mark.parametrize(
    "fixture_name", [None, "task_success.json", "task_v10_success.json"]
)
async def test_reads_tasks_json(
    fixture_name: str | None, load_fixture: Callable[[str], Any]
) -> None:
    tasks = [Task.model_validate(load_fixture(fixture_name))] if fixture_name else []
    upstream = MagicMock()
    upstream.tasks.list = AsyncMock(
        return_value=Paginated[Task](count=len(tasks), results=tasks)
    )
    mcp = FastMCP("test")
    ctx = ToolContext(client=upstream, default_page_size=25, public_url="")
    tasks_mod.register(mcp, ctx)

    async with Client(mcp) as client:
        resources = await client.list_resources()
        resource = next(r for r in resources if str(r.uri) == "tasks://paperless")
        assert resource.mime_type == "application/json"
        contents = await client.read_resource("tasks://paperless")

    assert len(contents) == 1
    content = contents[0]
    assert isinstance(content, TextResourceContents)
    assert content.mime_type == "application/json"
    result = json.loads(content.text)
    upstream.tasks.list.assert_awaited_once_with()
    if fixture_name is None:
        assert result == []
        return

    assert len(result) == 1
    task = result[0]
    expected = load_fixture(fixture_name)
    assert task["date_created"] == expected["date_created"]
    assert task["date_done"] == expected["date_done"]
    assert task["status"] == "SUCCESS"
    assert task["related_document"] == "42"
    if fixture_name == "task_v10_success.json":
        assert task["date_started"] == expected["date_started"]
        assert task["result_data"] == {"document_id": 42}
        assert task["input_data"] == {"filename": "invoice.pdf"}
        assert task["related_document_ids"] == [42]
        assert task["owner"] == 1
    else:
        assert task["date_started"] is None
        assert task["result_data"] is None
