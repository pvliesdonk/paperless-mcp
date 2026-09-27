"""Pydantic models for Paperless-NGX document type resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paperless_mcp.models._compat import UserId
from paperless_mcp.models._fields import IsInsensitive, Match, MatchingAlgorithm


class DocumentType(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    document_count: int | None = None
    owner: UserId = None
    user_can_change: bool = True


class DocumentTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(
        ..., min_length=1, description="Document type name, such as Invoice."
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None


class DocumentTypePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(
        default=None, description="New name; omit to keep the current one."
    )
    match: Match = None
    matching_algorithm: MatchingAlgorithm = None
    is_insensitive: IsInsensitive = None
