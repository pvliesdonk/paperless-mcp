"""Shared Pydantic models used across resource modules."""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import Generic, Literal, TypeVar
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _normalise_page_marker(value: str | None) -> str | None:
    """Return ``page=N`` for any URL or query fragment, ``None`` otherwise.

    Paperless-paginated endpoints echo back upstream URLs like
    ``http://paperless-ngx:8000/api/documents/?page=2`` which leak the internal
    hostname and are inconsistent with client-paginated endpoints (see #32).
    Normalising here guarantees both shapes collapse to ``page=2``.
    """
    if value is None:
        return None
    # Accept full URL or bare query fragment. ``urlparse`` only populates
    # ``.query`` when a scheme/netloc is present, so fall back to the raw value.
    query = urlparse(value).query or value
    pages = parse_qs(query).get("page")
    if pages and pages[0].isdigit():
        return f"page={pages[0]}"
    # Surface unexpected shapes (cursor/offset pagination, malformed URLs) at
    # WARNING so the normalised ``None`` — which otherwise silently stops
    # pagination — is traceable in production.
    logger.warning("normalise_page_marker unexpected_shape value=%r", value)
    return None


class Paginated(BaseModel, Generic[T]):
    # extra="ignore" drops Paperless's upstream ``all: [...]`` id array (see #25).
    model_config = ConfigDict(extra="ignore")
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[T] = Field(default_factory=list)

    @field_validator("next", "previous", mode="after")
    @classmethod
    def _strip_upstream_url(cls, value: str | None) -> str | None:
        return _normalise_page_marker(value)


class ListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
    ordering: str | None = None


class BulkEditOperation(StrEnum):
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
