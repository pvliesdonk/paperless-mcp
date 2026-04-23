from __future__ import annotations

import asyncio
import time

from paperless_mcp.client._http import PaperlessHTTP
from paperless_mcp.models.task import Task, TaskStatus

_TERMINAL_STATUSES = {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.REVOKED}


class TasksClient:
    def __init__(self, http: PaperlessHTTP) -> None:
        self._http = http

    async def list(
        self, *, status: TaskStatus | None = None, acknowledged: bool | None = None
    ) -> list[Task]:
        body = await self._http.get_json("/api/tasks/")
        result = [Task.model_validate(entry) for entry in body]
        if status is not None:
            result = [t for t in result if t.status is status]
        if acknowledged is not None:
            result = [t for t in result if t.acknowledged is acknowledged]
        return result

    async def get(self, task_uuid: str) -> Task | None:
        for task in await self.list():
            if task.task_id == task_uuid:
                return task
        return None

    async def wait_for(
        self,
        task_uuid: str,
        *,
        timeout_seconds: float = 60.0,
        poll_seconds: float = 1.0,
    ) -> Task:
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
