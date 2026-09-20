"""MCP tool registrations for Paperless tasks (read-only)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskStatus, TaskType
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register task tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_tasks"))
    @paperless_errors
    async def list_tasks(
        page: Annotated[int, Field(ge=1)] = 1,
        page_size: Annotated[int, Field(ge=1, le=100)] = ctx.default_page_size,
        status: TaskStatus | None = None,
        task_type: TaskType | None = None,
        acknowledged: bool | None = None,
        include_acknowledged: bool = False,
    ) -> Paginated[Task]:
        """List Paperless Celery tasks.

        Defaults to unacknowledged tasks only (set ``include_acknowledged=True``
        or ``acknowledged=True`` to see acknowledged ones).  Returns one page,
        newest first.

        Pass ``task_type`` to filter by the kind of work — ``"bulk_update"``
        is the search-index rebuild that ``bulk_edit_documents`` queues, so
        that tool's deferred indexing can be waited on with ``wait_for_task``.
        Version 10 adds task_type, trigger_source, structured result_data,
        related_document_ids and timing fields. Statuses retain their uppercase
        spelling. Legacy task_name, type, result and related_document remain
        compatibility projections; use the v10 fields for full detail.
        """
        return await client.tasks.list(
            page=page,
            page_size=page_size,
            status=status,
            task_type=task_type,
            acknowledged=acknowledged,
            include_acknowledged=include_acknowledged,
        )

    @mcp.tool(**tool_metadata("get_task"))
    @paperless_errors
    async def get_task(task_uuid: str) -> Task | None:
        """Fetch a task by UUID.  Returns ``None`` if no such task exists."""
        return await client.tasks.get(task_uuid)

    @mcp.tool(**tool_metadata("wait_for_task"))
    @paperless_errors
    async def wait_for_task(
        task_uuid: str,
        timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 60.0,
    ) -> Task:
        """Poll until the task reaches a terminal state or times out."""
        return await client.tasks.wait_for(task_uuid, timeout_seconds=timeout_seconds)
