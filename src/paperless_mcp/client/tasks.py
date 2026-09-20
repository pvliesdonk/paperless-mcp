"""Tasks resource client.

Payload version 10 supplies server-paginated envelopes; version 9 fallback
supplies bare arrays paginated locally. UUID lookup and waiting accept both.
See ``docs/design/reference/paperless-api-versioning.md``.

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

        Version 10 paginates on the server. Version 9 returns a bare array,
        which is sliced locally after the HTTP layer adapts its query filters.

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
                bulk edit queues. The HTTP boundary translates this filter
                to the legacy task_name spelling on version 9 instances.

        Returns:
            A :class:`Paginated` page of :class:`Task` objects.
        """
        params: dict[str, object] = {"page": page, "page_size": page_size}
        if status is not None:
            params["status"] = status.value.lower()
        if task_type is not None:
            params["task_type"] = task_type.value
        if acknowledged is None and not include_acknowledged:
            acknowledged = False
        if acknowledged is not None:
            params["acknowledged"] = str(acknowledged).lower()
        body = await self._http.get_json("/api/tasks/", params=params)
        if isinstance(body, dict):
            return Paginated[Task].model_validate(body)
        # Version 9 instances return an unpaginated list.
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
        items = body.get("results", []) if isinstance(body, dict) else body
        if items and isinstance(items, builtins.list):
            return Task.model_validate(items[0])
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
