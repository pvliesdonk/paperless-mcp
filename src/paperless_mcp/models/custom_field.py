"""Pydantic models for Paperless-NGX custom field resources."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CustomFieldDataType(StrEnum):
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
    name: str = Field(..., min_length=1, description="Field name.")
    data_type: CustomFieldDataType = Field(
        description="Kind of value the field holds; fixed once created."
    )
    extra_data: Any | None = Field(
        default=None,
        description=(
            'For select, required: {"select_options": [{"label": "Low"}, '
            '{"label": "High"}]}; Paperless gives each option an id. For '
            'monetary, optional: {"default_currency": "EUR"}. Omit for every '
            "other type."
        ),
    )


class CustomFieldPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(
        default=None, description="New name; omit to keep the current one."
    )
    extra_data: Any | None = Field(
        default=None,
        description=(
            "Omit to keep the current options. For select, select_options "
            "replaces the whole list: list every option to keep with its id "
            '({"id": "abc", "label": "Low"}), add new ones without an id, and '
            "leave out the ones to delete, which also clears them from "
            'documents. For monetary: {"default_currency": "EUR"}.'
        ),
    )
