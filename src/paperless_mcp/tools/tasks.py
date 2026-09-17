"""MCP tool registrations for Paperless tasks (read-only)."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskStatus
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register task tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client
    jobs = ctx.jobs  # SPIKE (#110)

    @register_tool(mcp, "list_tasks")
    async def list_tasks(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        status: TaskStatus | None = None,
        acknowledged: bool | None = None,
        include_acknowledged: bool = False,
    ) -> Paginated[Task]:
        """List Paperless Celery tasks.

        Defaults to unacknowledged tasks only (set ``include_acknowledged=True``
        or ``acknowledged=True`` to see acknowledged ones).  Returns one page.
        """
        return await client.tasks.list(
            page=page,
            page_size=page_size,
            status=status,
            acknowledged=acknowledged,
            include_acknowledged=include_acknowledged,
        )

    @register_tool(mcp, "get_task")
    async def get_task(task_uuid: str) -> Task | None:
        """Fetch a task by UUID.  Returns ``None`` if no such task exists."""
        return await client.tasks.get(task_uuid)

    # SPIKE (#110): path 2 (`build_jobs` + `run_with_deadline`), not path 1
    # (`register_long_running_tool`).  Path 1 registers the tool itself via
    # `mcp.tool`, which would bypass this repo's `register_tool` — losing the
    # icon and annotation registries and the Paperless error-to-ToolError
    # wrapper.  Composing on path 2 keeps all three.
    #
    # The declared return type has to widen from `Task` to `dict[str, Any]`,
    # because the caller now receives either the task or a job handle.  That
    # is the one unavoidable surface cost: the typed output schema is gone.
    @register_tool(mcp, "wait_for_task")
    async def wait_for_task(
        task_uuid: str,
        timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 60.0,
    ) -> dict[str, Any]:
        """Poll until the task reaches a terminal state or times out."""

        async def _wait() -> dict[str, Any]:
            task = await client.tasks.wait_for(
                task_uuid, timeout_seconds=timeout_seconds
            )
            return task.model_dump(mode="json")

        if jobs is None:
            return await _wait()
        result: dict[str, Any] = await jobs.run_with_deadline(
            _wait(), tool="wait_for_task"
        )
        return result
