"""MCP tool registrations for Paperless tasks (read-only)."""

from __future__ import annotations

import logging
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp_pvl_core import tool_boundary
from pydantic import Field

from paperless_mcp.client.tasks import TERMINAL_STATUSES
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskStatus, TaskType
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._errors import paperless_errors
from paperless_mcp.tools._metadata import tool_metadata
from paperless_mcp.tools._params import Page, PageSize


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register task tools on *mcp*.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with the Paperless client and pagination defaults.
    """
    client = ctx.client

    @mcp.tool(**tool_metadata("list_tasks"))
    @tool_boundary
    @paperless_errors
    async def list_tasks(
        page: Page = 1,
        page_size: PageSize = ctx.default_page_size,
        status: TaskStatus | None = None,
        task_type: TaskType | None = None,
        acknowledged: bool | None = None,
        include_acknowledged: bool = False,
    ) -> Paginated[Task]:
        """List Paperless background tasks such as consuming uploads and reindexing; returns one page, newest first.

        Args:
            status: Keep tasks in this state.
            task_type: Keep tasks of this kind; bulk_update is the reindex that
                bulk_edit_documents' metadata operations start.
            acknowledged: Keep only acknowledged (true) or unacknowledged (false) tasks.
            include_acknowledged: Also list tasks already acknowledged; by default
                only unacknowledged ones are listed.
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
    @tool_boundary
    @paperless_errors
    async def get_task(task_uuid: str) -> Task | None:
        """Get one background task by id, with its status and result; returns null if there is none.

        Args:
            task_uuid: Task id, as returned by upload_document or listed by list_tasks.
        """
        return await client.tasks.get(task_uuid)

    @mcp.tool(**tool_metadata("wait_for_task"))
    @tool_boundary
    @paperless_errors
    async def wait_for_task(
        task_uuid: str,
        timeout_seconds: Annotated[float, Field(gt=0, le=600)] = 60.0,
    ) -> Task:
        """Wait for a background task to finish; returns the task with its final status and result.

        Args:
            task_uuid: Task id, as returned by upload_document or listed by list_tasks.
            timeout_seconds: Longest time to wait, up to 600 seconds.
        """
        try:
            return await client.tasks.wait_for(
                task_uuid, timeout_seconds=timeout_seconds
            )
        except TimeoutError as exc:
            # The poll ends the same way whether the task is still running or
            # never existed; one more read tells the two apart for the model,
            # and returns the task if it finished since the last poll.
            task = await client.tasks.get(task_uuid)
            if task is not None and task.status in TERMINAL_STATUSES:
                return task
            if task is None:
                message = (
                    f"Paperless has no task with id {task_uuid}. Find the id "
                    "with list_tasks, then call wait_for_task again."
                )
            else:
                message = (
                    f"Task {task_uuid} has not finished after {timeout_seconds:g} "
                    "seconds. Call wait_for_task again to keep waiting, or "
                    "get_task to read its current status."
                )
            raise ToolError(message, log_level=logging.INFO) from exc
