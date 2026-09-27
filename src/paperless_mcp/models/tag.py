"""Pydantic models for Paperless-NGX tag resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperless_mcp.models._compat import UserId
from paperless_mcp.models._fields import IsInsensitive, Match, MatchingAlgorithm


class Tag(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    # Paperless ≤1.x used integer `colour`; ≥2.x uses hex-string `color`.
    # Both may be present; accept either to support mixed-version instances.
    colour: int | None = None
    color: str | None = None
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    is_inbox_tag: bool = False
    document_count: int | None = None
    owner: UserId = None
    user_can_change: bool = True


class TagCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1, description="Tag name.")
    color: str | None = Field(
        default=None, description="Display colour as a hex code, such as #a6cee3."
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None
    is_inbox_tag: bool | None = Field(
        default=None,
        description=(
            "Make this an inbox tag, which Paperless adds to every newly "
            "consumed document."
        ),
    )


class TagPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(
        default=None, description="New name; omit to keep the current one."
    )
    color: str | None = Field(
        default=None, description="Display colour as a hex code, such as #a6cee3."
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None
    is_inbox_tag: bool | None = Field(
        default=None,
        description=(
            "Make this an inbox tag, which Paperless adds to every newly "
            "consumed document."
        ),
    )
