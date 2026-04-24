"""Compatibility helpers for Paperless-NGX schema variations."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator


def _coerce_user_id(value: Any) -> Any:
    """Collapse a user reference down to its integer ID.

    Newer Paperless-NGX releases return ``user`` / ``owner`` fields as a
    nested object like ``{"id": 3, "username": "alice", ...}`` where older
    releases returned just ``3``.  We surface only the ID downstream, so
    extract it when we see the dict form.  Returns the input unchanged
    otherwise (covering ``None`` and the bare-int legacy shape).
    """
    if isinstance(value, dict):
        return value.get("id")
    return value


def _coerce_username(value: Any) -> Any:
    """Collapse a user reference down to its username string.

    Same schema drift as ``_coerce_user_id`` but for fields that historically
    held a username string (e.g. audit-log ``actor``).  Newer Paperless
    returns ``{"id": 3, "username": "alice", ...}``; we extract the
    ``username`` so the field's contract stays a plain string.
    """
    if isinstance(value, dict):
        return value.get("username")
    return value


UserId = Annotated[int | None, BeforeValidator(_coerce_user_id)]
Username = Annotated[str | None, BeforeValidator(_coerce_username)]
