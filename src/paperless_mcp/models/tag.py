from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

class Tag(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    slug: str | None = None
    name: str
    colour: int | None = None
    color: str | None = None
    match: str | None = ""
    matching_algorithm: int | None = None
    is_insensitive: bool = True
    is_inbox_tag: bool = False
    document_count: int | None = None
    owner: int | None = None
    user_can_change: bool = True

class TagCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1)
    color: str | None = None
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None
    is_inbox_tag: bool | None = None

class TagPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    color: str | None = None
    match: str | None = None
    matching_algorithm: int | None = None
    is_insensitive: bool | None = None
    is_inbox_tag: bool | None = None
