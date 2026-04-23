from __future__ import annotations
import httpx, pytest, respx
from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.client.tasks import TasksClient
from paperless_mcp.models.task import TaskStatus

@pytest.fixture
async def http():
    client = PaperlessHTTP(base_url="http://paperless.test", api_token="t", max_retries=0)
    yield client
    await client.aclose()

@pytest.fixture
def tasks(http: PaperlessHTTP) -> TasksClient:
    return TasksClient(http)

@pytest.mark.asyncio
async def test_list_all(tasks: TasksClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[load_fixture("task_pending.json")]))
        result = await tasks.list()
    assert result[0].status is TaskStatus.PENDING

@pytest.mark.asyncio
async def test_get_by_uuid_uses_list_filter(tasks: TasksClient, load_fixture) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[load_fixture("task_success.json")]))
        task = await tasks.get("abc-123-success")
    assert task is not None
    assert task.status is TaskStatus.SUCCESS

@pytest.mark.asyncio
async def test_get_unknown_returns_none(tasks: TasksClient) -> None:
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[]))
        task = await tasks.get("nope")
    assert task is None

@pytest.mark.asyncio
async def test_wait_for_resolves_success(tasks: TasksClient, load_fixture) -> None:
    pending = load_fixture("task_pending.json")
    success = load_fixture("task_success.json")
    success["task_id"] = pending["task_id"]
    responses = [httpx.Response(200, json=[pending]), httpx.Response(200, json=[pending]), httpx.Response(200, json=[success])]
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(side_effect=responses)
        task = await tasks.wait_for(pending["task_id"], timeout_seconds=2, poll_seconds=0.01)
    assert task.status is TaskStatus.SUCCESS

@pytest.mark.asyncio
async def test_wait_for_times_out(tasks: TasksClient, load_fixture) -> None:
    pending = load_fixture("task_pending.json")
    async with respx.mock(base_url="http://paperless.test") as mock:
        mock.get("/api/tasks/").mock(return_value=httpx.Response(200, json=[pending]))
        with pytest.raises(TimeoutError):
            await tasks.wait_for(pending["task_id"], timeout_seconds=0.05, poll_seconds=0.01)
