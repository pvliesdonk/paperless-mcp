"""Task models exposing payload v10 data while preserving released v9 fields.

See docs/design/reference/paperless-api-versioning.md and
docs/design/task-payloads.md for compatibility and pagination decisions.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from paperless_mcp.models._compat import (
    OptionalPaperlessDatetime,
    PaperlessDatetime,
    RelatedDocumentId,
)
from paperless_mcp.models._task_compat import normalize_task_payload


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"

    @classmethod
    def _missing_(cls, value: object) -> TaskStatus | None:
        if isinstance(value, str):
            return cls.__members__.get(value.upper())
        return None


class TaskType(StrEnum):
    """Kinds of background work Paperless records in ``/api/tasks/``.

    These are payload version 10 spellings. On version 9 fallback, the HTTP
    boundary translates the filter to task_name and maps sanity_check to
    check_sanity and llm_index to llmindex_update. Not every task kind exists
    on Paperless 2.x. See
    ``docs/design/reference/paperless-bulk-edit-indexing.md``.
    """

    CONSUME_FILE = "consume_file"
    TRAIN_CLASSIFIER = "train_classifier"
    SANITY_CHECK = "sanity_check"
    INDEX_OPTIMIZE = "index_optimize"
    MAIL_FETCH = "mail_fetch"
    LLM_INDEX = "llm_index"
    EMPTY_TRASH = "empty_trash"
    CHECK_WORKFLOWS = "check_workflows"
    BULK_UPDATE = "bulk_update"
    REPROCESS_DOCUMENT = "reprocess_document"
    BUILD_SHARE_LINK = "build_share_link"
    BULK_DELETE = "bulk_delete"
    APPLY_AI_SUGGESTIONS = "apply_ai_suggestions"


class Task(BaseModel):
    """Task details with structured results and compatible legacy projections."""

    @model_validator(mode="before")
    @classmethod
    def _normalize_payload(cls, value: Any) -> Any:
        return normalize_task_payload(value)

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

    task_type: str | None = None
    task_type_display: str | None = None
    trigger_source: str | None = None
    trigger_source_display: str | None = None
    status_display: str | None = None
    date_started: OptionalPaperlessDatetime = None
    duration_seconds: float | None = None
    wait_time_seconds: float | None = None
    input_data: dict[str, Any] | None = None
    result_data: dict[str, Any] | None = None
    related_document_ids: list[int] = Field(default_factory=list)
