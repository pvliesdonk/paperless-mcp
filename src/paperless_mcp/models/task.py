from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

class Task(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    task_id: str
    task_file_name: str | None = None
    date_created: datetime
    date_done: datetime | None = None
    type: str | None = None
    status: TaskStatus
    result: str | None = None
    acknowledged: bool = False
    related_document: str | None = None
