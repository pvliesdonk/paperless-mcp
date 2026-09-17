"""Pydantic models for Paperless-NGX share link resources."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from paperless_mcp.models._compat import OptionalPaperlessDatetime, PaperlessDatetime


class ShareLinkFileVersion(StrEnum):
    ARCHIVE = "archive"
    ORIGINAL = "original"


class ShareLink(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    created: PaperlessDatetime
    expiration: OptionalPaperlessDatetime = None
    slug: str
    document: int
    file_version: ShareLinkFileVersion
    share_url: str | None = None
