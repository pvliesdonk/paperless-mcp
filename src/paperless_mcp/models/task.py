"""Pydantic models for Paperless-NGX task resources.

These fields follow Paperless payload version 9, which ``client/_http.py``
pins.  Version 10 renames ``result``, ``type`` and ``related_document`` and
serves lowercase statuses that :class:`TaskStatus` would reject.  See
``docs/design/reference/paperless-api-versioning.md``.

:class:`TaskType` is the exception: it names query-filter values rather than
response fields, and those Paperless accepts under their version 10 spellings
at both versions.
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


class TaskType(StrEnum):
    """Kinds of background work Paperless records in ``/api/tasks/``.

    These are the payload version 10 spellings, which the ``?task_type=``
    query filter accepts at both payload versions.  Version 9 *responses*
    still spell two of them differently — ``sanity_check`` arrives as
    ``check_sanity`` and ``llm_index`` as ``llmindex_update``.  See
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
