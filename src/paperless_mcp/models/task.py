"""Pydantic models for Paperless-NGX task resources."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from paperless_mcp.models._compat import (
    AwareDatetime,
    OptionalAwareDatetime,
    RelatedDocumentId,
)


class TaskStatus(StrEnum):
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
    date_created: AwareDatetime
    date_done: OptionalAwareDatetime = None
    type: str | None = None
    status: TaskStatus
    result: str | None = None
    acknowledged: bool = False
    related_document: RelatedDocumentId = None
