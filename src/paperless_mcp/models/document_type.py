"""Pydantic models for Paperless-NGX document type resources."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentType(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool = True


class DocumentTypeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1)
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None


class DocumentTypePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None
