from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class CustomFieldDataType(str, Enum):
    STRING = "string"
    LONGTEXT = "longtext"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    DATE = "date"
    MONETARY = "monetary"
    URL = "url"
    DOCUMENTLINK = "documentlink"
    SELECT = "select"

class CustomField(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    name: str
    data_type: CustomFieldDataType
    extra_data: Any | None = None

class CustomFieldCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1)
    data_type: CustomFieldDataType
    extra_data: Any | None = None

class CustomFieldPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    extra_data: Any | None = None
