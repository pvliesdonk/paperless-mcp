"""Pydantic models for Paperless-NGX task resources.

These fields follow Paperless payload version 9, which ``client/_http.py``
pins.  Version 10 renames ``result``, ``type`` and ``related_document`` and
serves lowercase statuses that :class:`TaskStatus` would reject.  See
``docs/design/reference/paperless-api-versioning.md``.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from paperless_mcp.models._compat import (
    OptionalPaperlessDatetime,
    PaperlessDatetime,
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
    date_created: PaperlessDatetime
    date_done: OptionalPaperlessDatetime = None
    type: str | None = None
    status: TaskStatus
    result: str | None = None
    acknowledged: bool = False
    related_document: RelatedDocumentId = None
