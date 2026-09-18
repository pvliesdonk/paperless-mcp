"""Tasks resource client.

The bare-array response this module paginates client-side is specific to
Paperless payload version 9, which ``client/_http.py`` pins.  Version 10
returns a paginated envelope instead, which would make :meth:`TasksClient.list`
iterate the envelope's keys and :meth:`TasksClient.get` return ``None`` for
every lookup.  See ``docs/design/reference/paperless-api-versioning.md``.

The ``task_type`` filter is what makes deferred work observable — notably the
``bulk_update`` rebuild a bulk edit queues after answering ``OK``.  See
``docs/design/reference/paperless-bulk-edit-indexing.md``.
"""

from __future__ import annotations

import asyncio
import builtins
import time

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.common import Paginated
from paperless_mcp.models.task import Task, TaskStatus, TaskType

_TERMINAL_STATUSES = {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED}


class TasksClient:
    """Async operations against ``/api/tasks/``."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        status: TaskStatus | None = None,
        task_type: TaskType | None = None,
        acknowledged: bool | None = None,
        include_acknowledged: bool = False,
    ) -> Paginated[Task]:
        """List Paperless tasks with pagination and optional filtering.

        The ``/api/tasks/`` endpoint returns a bare JSON array (no paginated
        envelope), so pagination is performed client-side: all matching tasks
        are fetched in one request and sliced here.

        Args:
            acknowledged: Filter by acknowledged flag.  When ``None`` and
                ``include_acknowledged`` is ``False``, defaults to ``False``
                (unacknowledged only).
            include_acknowledged: When ``True``, do not apply the default
                ``acknowledged=false`` filter.  Ignored if *acknowledged* is
                set explicitly.
            page: Page number (1-based).
            page_size: Results per page. Tool layer clamps 1-100.
            status: Filter by task status.
            task_type: Filter by kind of work, such as
                :attr:`TaskType.BULK_UPDATE` for the search-index rebuild a
                bulk edit queues.  Paperless honours this filter at payload
                version 9 as well as 10, even though version 9 responses
                carry the value under ``task_name``.

        Returns:
            A :class:`Paginated` page of :class:`Task` objects.
        """
        params: dict[str, object] = {}
        if status is not None:
            params["status"] = status.value
        if task_type is not None:
            params["task_type"] = task_type.value
        if acknowledged is None and not include_acknowledged:
            acknowledged = False
        if acknowledged is not None:
            params["acknowledged"] = str(acknowledged).lower()
        body = await self._http.get_json("/api/tasks/", params=params)
        # /api/tasks/ returns a bare list — paginate client-side.
        all_tasks = [Task.model_validate(item) for item in body]
        start = (page - 1) * page_size
        end = start + page_size
        total = len(all_tasks)
        next_marker = f"page={page + 1}" if end < total else None
        previous_marker = f"page={page - 1}" if page > 1 else None
        return Paginated[Task].model_validate(
            {
                "count": total,
                "next": next_marker,
                "previous": previous_marker,
                "results": [t.model_dump() for t in all_tasks[start:end]],
            }
        )

    async def get(self, task_uuid: str) -> Task | None:
        """Fetch a single task by UUID.

        Args:
            task_uuid: The task UUID to look up.

        Returns:
            The matching :class:`Task`, or ``None`` if not found.
        """
        body = await self._http.get_json("/api/tasks/", params={"task_id": task_uuid})
        if body and isinstance(body, builtins.list):
            return Task.model_validate(body[0])
        return None

    async def wait_for(
        self,
        task_uuid: str,
        *,
        timeout_seconds: float = 60.0,
        poll_seconds: float = 1.0,
    ) -> Task:
        """Poll until a task reaches a terminal status.

        Args:
            task_uuid: UUID of the task to wait for.
            timeout_seconds: Maximum time to wait before raising :exc:`TimeoutError`.
            poll_seconds: Seconds between polls.

        Returns:
            The completed :class:`Task`.

        Raises:
            TimeoutError: If the task does not complete within ``timeout_seconds``.
        """
        deadline = time.monotonic() + timeout_seconds
        while True:
            task = await self.get(task_uuid)
            if task is not None and task.status in _TERMINAL_STATUSES:
                return task
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"task {task_uuid} did not complete within {timeout_seconds}s"
                )
            await asyncio.sleep(poll_seconds)
