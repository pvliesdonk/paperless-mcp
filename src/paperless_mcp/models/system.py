from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class Statistics(BaseModel):
    model_config = ConfigDict(extra="allow")
    documents_total: int | None = None
    documents_inbox: int | None = None
    inbox_tag: int | None = None
    document_file_type_counts: list[dict[str, Any]] = Field(default_factory=list)
    character_count: int | None = None
    tag_count: int | None = None
    correspondent_count: int | None = None
    document_type_count: int | None = None
    storage_path_count: int | None = None
    current_asn: int | None = None

class RemoteVersion(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: str
    update_available: bool = False
