"""Pydantic models for Paperless-NGX correspondent resources."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from paperless_mcp.models._compat import UserId


class Correspondent(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    document_count: int | None = None
    last_correspondence: datetime | None = None
    owner: UserId = None
    user_can_change: bool = True


class CorrespondentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1)
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None


class CorrespondentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None
