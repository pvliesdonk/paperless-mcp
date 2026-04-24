"""Tasks resource client."""

from __future__ import annotations

import asyncio
import builtins
import time

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.task import Task, TaskStatus

_TERMINAL_STATUSES = {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED}


class TasksClient:
    """Async operations against ``/api/tasks/``."""

    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self, *, status: TaskStatus | None = None, acknowledged: bool | None = None
    ) -> builtins.list[Task]:
        """List tasks with optional server-side filtering.

        Args:
            status: Filter by task status.
            acknowledged: Filter by acknowledged flag.

        Returns:
            List of matching :class:`Task` objects.
        """
        params: dict[str, object] = {}
        if status is not None:
            params["status"] = status.value
        if acknowledged is not None:
            params["acknowledged"] = str(acknowledged).lower()
        body = await self._http.get_json("/api/tasks/", params=params or None)
        return [Task.model_validate(entry) for entry in body]

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
