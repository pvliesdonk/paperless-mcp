"""Compatibility helpers for Paperless-NGX schema variations."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BeforeValidator

logger = logging.getLogger(__name__)


def _coerce_user_id(value: Any) -> Any:
    """Collapse a user reference down to its integer ID.

    Newer Paperless-NGX releases return ``user`` / ``owner`` fields as a
    nested object like ``{"id": 3, "username": "alice", ...}`` where older
    releases returned just ``3``.  We surface only the ID downstream, so
    extract it when we see the dict form.  Returns the input unchanged
    otherwise (covering ``None`` and the bare-int legacy shape).

    If the dict is missing the ``"id"`` key, return the original dict so
    Pydantic raises a ``ValidationError`` — silently coercing to ``None``
    would hide upstream schema drift.
    """
    if isinstance(value, dict):
        return value.get("id", value)
    return value


def _coerce_username(value: Any) -> Any:
    """Collapse a user reference down to its username string.

    Same schema drift as ``_coerce_user_id`` but for fields that historically
    held a username string (e.g. audit-log ``actor``).  Newer Paperless
    returns ``{"id": 3, "username": "alice", ...}``; we extract the
    ``username`` so the field's contract stays a plain string.

    If the dict is missing the ``"username"`` key, return the original
    dict so Pydantic raises a ``ValidationError`` instead of silently
    dropping the field.
    """
    if isinstance(value, dict):
        return value.get("username", value)
    return value


def _ensure_aware(value: datetime | None) -> datetime | None:
    """Attach UTC to a naive datetime so it keeps an explicit offset.

    Paperless-NGX can return a date-only value (e.g. a document ``created``
    date set without a time) for a field typed ``datetime``.  Pydantic
    parses that leniently into a naive ``datetime``, which then
    round-trips without a timezone offset and fails strict RFC 3339
    ``format: date-time`` validation downstream.  Attaching UTC keeps the
    wall-clock value unchanged while making the offset explicit.
    """
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _coerce_related_document(value: Any) -> Any:
    """Stringify an integer ``related_document`` task reference.

    Newer Paperless-NGX releases return this field as the document's
    integer ID; the field's contract is a string ID, so coerce an int to
    its string form.  Returns the input unchanged otherwise.
    """
    if isinstance(value, int):
        return str(value)
    return value


UserId = Annotated[int | None, BeforeValidator(_coerce_user_id)]
Username = Annotated[str | None, BeforeValidator(_coerce_username)]
PaperlessDatetime = Annotated[datetime, AfterValidator(_ensure_aware)]
OptionalPaperlessDatetime = Annotated[datetime | None, AfterValidator(_ensure_aware)]
RelatedDocumentId = Annotated[str | None, BeforeValidator(_coerce_related_document)]
