"""Pydantic models for Paperless-NGX system-level resources."""

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
    """``/api/remote_version/``: the newest release published on GitHub.

    ``version`` is the latest release tag Paperless fetched from GitHub (its
    own 15-minute cache, ``"0.0.0"`` when that fetch failed), **not** the
    version of the instance answering the call.  Paperless parses its running
    version only to compute ``update_available`` and never returns it.
    [verified: paperless-ngx ``src/documents/views.py``, ``RemoteVersionView``
    at ae9529551d17]  For the running version see :class:`UiSettingsResponse`.
    """

    model_config = ConfigDict(extra="allow")
    version: str
    update_available: bool = False


class UiSettings(BaseModel):
    """The ``settings`` member of ``/api/ui_settings/``.

    Only ``version`` is declared: the rest of that object is the web UI's own
    state and is not this server's business.  ``extra="allow"`` keeps it rather
    than dropping it, so a caller that needs another key can reach it.

    Attributes:
        version: The Paperless-NGX version *installed on the instance*, which
            Paperless fills from its own ``__full_version_str__``.
    """

    model_config = ConfigDict(extra="allow")
    version: str


class UiSettingsResponse(BaseModel):
    """``/api/ui_settings/``: the envelope around :class:`UiSettings`.

    [verified: paperless-ngx ``src/documents/views.py``, ``UiSettingsView``
    at ae9529551d17, where ``ui_settings["version"]`` is set from
    ``version.__full_version_str__`` and returned under ``settings``.]
    """

    model_config = ConfigDict(extra="allow")
    settings: UiSettings
