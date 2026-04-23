"""Shared Pydantic models used across resource modules."""
from __future__ import annotations
from enum import Enum
from typing import Any, Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class Paginated(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="allow")
    count: int
    next: str | None = None
    previous: str | None = None
    all: list[int] | None = None
    results: list[T] = Field(default_factory=list)

class ListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
    ordering: str | None = None

class BulkEditOperation(str, Enum):
    SET_CORRESPONDENT = "set_correspondent"
    SET_DOCUMENT_TYPE = "set_document_type"
    SET_STORAGE_PATH = "set_storage_path"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    MODIFY_TAGS = "modify_tags"
    DELETE = "delete"
    REDO_OCR = "redo_ocr"
    SET_PERMISSIONS = "set_permissions"
    MERGE = "merge"
    SPLIT = "split"
    ROTATE = "rotate"
    DELETE_PAGES = "delete_pages"
    MODIFY_CUSTOM_FIELDS = "modify_custom_fields"

class BulkEditResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    result: Literal["OK"] | str

class UploadTaskAcknowledgement(BaseModel):
    model_config = ConfigDict(extra="allow")
    task_id: str

class DownloadLink(BaseModel):
    model_config = ConfigDict(extra="forbid")
    download_url: str
    expires_in_seconds: int
    content_type: str
    filename: str

def _ensure_extra_allow(data: dict[str, Any]) -> dict[str, Any]:
    return data
