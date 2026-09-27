"""Pydantic models for Paperless-NGX correspondent resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperless_mcp.models._compat import OptionalPaperlessDatetime, UserId
from paperless_mcp.models._fields import IsInsensitive, Match, MatchingAlgorithm


class Correspondent(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    document_count: int | None = None
    last_correspondence: OptionalPaperlessDatetime = None
    owner: UserId = None
    user_can_change: bool = True


class CorrespondentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(
        ...,
        min_length=1,
        description="Correspondent name, as it should appear on documents.",
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None


class CorrespondentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(
        default=None, description="New name; omit to keep the current one."
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None
