"""Pydantic models for Paperless-NGX document-related resources."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from paperless_mcp.models._compat import UserId, Username

_CONTENT_REDACTED_MARKER = "<content redacted — use get_document_content>"


class CustomFieldInstance(BaseModel):
    model_config = ConfigDict(extra="allow")
    field: int
    value: Any = None


class DocumentNote(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    # ``note`` is nullable on list/search responses where it's stripped for
    # payload size (see #30); single-document note endpoints return the full
    # text.
    note: str | None = None
    created: datetime
    user: UserId = None


class Document(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    title: str
    content: str | None = None
    tags: list[int] = Field(default_factory=list)
    created: datetime
    created_date: date | None = None
    modified: datetime | None = None
    added: datetime | None = None
    archive_serial_number: str | int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    owner: UserId = None
    user_can_change: bool = True
    notes: list[DocumentNote] = Field(default_factory=list)
    custom_fields: list[CustomFieldInstance] = Field(default_factory=list)
    page_count: int | None = None
    web_url: str | None = None


class DocumentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    tags: list[int] | None = None
    content: str | None = None
    archive_serial_number: str | int | None = None
    created: datetime | None = None
    created_date: date | None = None
    custom_fields: list[CustomFieldInstance] | None = None


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")
    original_checksum: str | None = None
    original_size: int | None = None
    original_mime_type: str | None = None
    media_filename: str | None = None
    has_archive_version: bool | None = None
    archive_checksum: str | None = None
    archive_media_filename: str | None = None
    original_filename: str | None = None
    archive_size: int | None = None
    lang: str | None = None
    original_metadata: list[dict[str, Any]] | None = None
    archive_metadata: list[dict[str, Any]] | None = None


class DocumentHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")
    timestamp: datetime
    action: str
    actor: Username = None
    changes: dict[str, Any] | None = None

    @field_validator("changes")
    @classmethod
    def _redact_content(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        # Redact OCR blobs from changes.content; preserve None/"None" lifecycle markers.
        if not value or "content" not in value:
            return value
        original = value["content"]
        if isinstance(original, list) and len(original) == 2:
            redacted = [
                v if v in (None, "None") else _CONTENT_REDACTED_MARKER for v in original
            ]
            return {**value, "content": redacted}
        return {**value, "content": _CONTENT_REDACTED_MARKER}


class DocumentSuggestions(BaseModel):
    model_config = ConfigDict(extra="allow")
    correspondents: list[int] = Field(default_factory=list)
    tags: list[int] = Field(default_factory=list)
    document_types: list[int] = Field(default_factory=list)
    storage_paths: list[int] = Field(default_factory=list)
    dates: list[date] = Field(default_factory=list)
