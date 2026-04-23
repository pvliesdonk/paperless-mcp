"""Pydantic models for Paperless-NGX share link resources."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ShareLinkFileVersion(StrEnum):
    ARCHIVE = "archive"
    ORIGINAL = "original"


class ShareLink(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    created: datetime
    expiration: datetime | None = None
    slug: str
    document: int
    file_version: ShareLinkFileVersion
