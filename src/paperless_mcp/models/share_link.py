from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class ShareLinkFileVersion(str, Enum):
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
