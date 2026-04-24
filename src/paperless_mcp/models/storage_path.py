"""Pydantic models for Paperless-NGX storage path resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from paperless_mcp.models._compat import UserId


class StoragePath(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    path: str
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    document_count: int | None = None
    owner: UserId = None
    user_can_change: bool = True
