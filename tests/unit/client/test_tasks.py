from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest
import respx

from paperless_mcp.client import PaperlessClient
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.tasks import TasksClient
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskStatus


@pytest.fixture
async def http():
    client = PaperlessHTTP(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    yield client
    await client.aclose()


@pytest.fixture
def tasks(http: PaperlessHTTP) -> TasksClient:
    return TasksClient(http)


@pytest.mark.asyncio
async def test_list_all(tasks: TasksClient, load_fixture) -> None:
    # /api/tasks/ returns a bare list; client-side pagination wraps it.
    bare = [load_fixture("task_pending.json")]
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=bare))
        result = await tasks.list()
    assert result.results[0].status is TaskStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_uuid_uses_list_filter(tasks: TasksClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tasks/").mock(
            return_value=httpx.Response(200, json=[load_fixture("task_success.json")])
        )
        task = await tasks.get("abc-123-success")
    assert task is not None
    assert task.status is TaskStatus.SUCCESS
    assert route.calls.last.request.url.params.get("task_id") == "abc-123-success"


@pytest.mark.asyncio
async def test_get_unknown_returns_none(tasks: TasksClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[]))
        task = await tasks.get("nope")
    assert task is None
    assert route.calls.last.request.url.params.get("task_id") == "nope"


@pytest.mark.asyncio
async def test_wait_for_resolves_success(tasks: TasksClient, load_fixture) -> None:
    pending = load_fixture("task_pending.json")
    success = load_fixture("task_success.json")
    success["task_id"] = pending["task_id"]
    responses = [
        httpx.Response(200, json=[pending]),
        httpx.Response(200, json=[pending]),
        httpx.Response(200, json=[success]),
    ]
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(side_effect=responses)
        task = await tasks.wait_for(
            pending["task_id"], timeout_seconds=2, poll_seconds=0.01
        )
    assert task.status is TaskStatus.SUCCESS


@pytest.mark.asyncio
async def test_wait_for_times_out(tasks: TasksClient, load_fixture) -> None:
    pending = load_fixture("task_pending.json")
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[pending]))
        with pytest.raises(TimeoutError):
            await tasks.wait_for(
                pending["task_id"], timeout_seconds=0.05, poll_seconds=0.01
            )


@pytest.mark.asyncio
async def test_list_tasks_paginated_defaults_to_unacknowledged(
    load_fixture: Callable[[str], Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/tasks/").mock(
            return_value=httpx.Response(200, json=load_fixture("tasks_page1.json"))
        )
        client = PaperlessClient(
            base_url=paperless_base_url, api_token=paperless_api_token
        )
        try:
            result = await client.tasks.list()
        finally:
            await client.aclose()

    assert route.called
    call = route.calls[0].request
    assert call.url.params.get("acknowledged") == "false"
    # page/page_size are NOT sent to the server; pagination is client-side.
    assert "page" not in call.url.params
    assert "page_size" not in call.url.params
    assert isinstance(result, Paginated)
    # count == total tasks in the bare list returned by /api/tasks/
    assert result.count == 2
    assert len(result.results) == 2
    assert all(isinstance(t, Task) for t in result.results)


@pytest.mark.asyncio
async def test_list_tasks_acknowledged_none_sends_no_filter(
    load_fixture: Callable[[str], Any],
    paperless_base_url: str,
    paperless_api_token: str,
) -> None:
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/tasks/").mock(
            return_value=httpx.Response(200, json=load_fixture("tasks_page1.json"))
        )
        client = PaperlessClient(
            base_url=paperless_base_url, api_token=paperless_api_token
        )
        try:
            await client.tasks.list(acknowledged=None, include_acknowledged=True)
        finally:
            await client.aclose()

    assert route.called
    call = route.calls[0].request
    assert "acknowledged" not in call.url.params
