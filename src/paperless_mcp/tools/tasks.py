"""MCP tool registrations for Paperless tasks (read-only)."""

from __future__ import annotations

from typing import Annotated

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
        ctx: Tool context with client and read-only flag.
    """
    client = ctx.client
    read_only = ctx.read_only

    @register_tool(mcp, "list_tasks", read_only_mode=read_only)
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

    @register_tool(mcp, "get_task", read_only_mode=read_only)
    async def get_task(task_uuid: str) -> Task | None:
        """Fetch a task by UUID.  Returns ``None`` if no such task exists."""
        return await client.tasks.get(task_uuid)

    @register_tool(mcp, "wait_for_task", read_only_mode=read_only)
    async def wait_for_task(
        task_uuid: str,
        timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 60.0,
    ) -> Task:
        """Poll until the task reaches a terminal state or times out."""
        return await client.tasks.wait_for(task_uuid, timeout_seconds=timeout_seconds)
