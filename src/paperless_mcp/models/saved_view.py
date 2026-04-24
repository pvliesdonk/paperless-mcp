"""Pydantic models for Paperless-NGX saved view resources."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from paperless_mcp.models._compat import UserId


class SavedView(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    name: str
    show_on_dashboard: bool = False
    show_in_sidebar: bool = False
    sort_field: str | None = None
    sort_reverse: bool = False
    filter_rules: list[dict[str, Any]] = Field(default_factory=list)
    page_size: int | None = None
    owner: UserId = None
