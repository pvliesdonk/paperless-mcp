"""Icon registry: tool name → list of :class:`mcp.types.Icon`.

Icons are Lucide SVGs stored under ``src/paperless_mcp/static/icons/``.
Names in the mapping match the registered MCP tool names exactly.
"""

from __future__ import annotations

from pathlib import Path

from mcp.types import Icon

from paperless_mcp.tools._registry import build_icon

_ICONS_DIR = Path(__file__).parent.parent / "static" / "icons"


def _icon(name: str) -> Icon:
    return build_icon(_ICONS_DIR / f"{name}.svg")


ICON_REGISTRY: dict[str, list[Icon]] = {
    # Documents — reads
    "list_documents": [_icon("files")],
    "search_documents": [_icon("search")],
    "get_document": [_icon("file-text")],
    "get_document_content": [_icon("type")],
    "get_document_thumbnail": [_icon("image")],
    "get_document_metadata": [_icon("info")],
    "get_document_notes": [_icon("message-square")],
    "get_document_history": [_icon("history")],
    "get_document_suggestions": [_icon("sparkles")],
    # Documents — writes
    "upload_document": [_icon("upload")],
    "update_document": [_icon("pencil")],
    "delete_document": [_icon("trash-2")],
    "bulk_edit_documents": [_icon("list-checks")],
    "add_document_note": [_icon("message-square-plus")],
    "delete_document_note": [_icon("message-square-x")],
    # Tags
    "list_tags": [_icon("tag")],
    "get_tag": [_icon("tag")],
    "create_tag": [_icon("tag")],
    "update_tag": [_icon("pencil")],
    "delete_tag": [_icon("trash-2")],
    "bulk_edit_tags": [_icon("list-checks")],
    # Correspondents
    "list_correspondents": [_icon("user")],
    "get_correspondent": [_icon("user")],
    "create_correspondent": [_icon("user-plus")],
    "update_correspondent": [_icon("pencil")],
    "delete_correspondent": [_icon("trash-2")],
    "bulk_edit_correspondents": [_icon("list-checks")],
    # Document types
    "list_document_types": [_icon("folder-tree")],
    "get_document_type": [_icon("folder-tree")],
    "create_document_type": [_icon("folder-tree")],
    "update_document_type": [_icon("pencil")],
    "delete_document_type": [_icon("trash-2")],
    "bulk_edit_document_types": [_icon("list-checks")],
    # Custom fields
    "list_custom_fields": [_icon("form-input")],
    "get_custom_field": [_icon("form-input")],
    "create_custom_field": [_icon("form-input")],
    "update_custom_field": [_icon("pencil")],
    "delete_custom_field": [_icon("trash-2")],
    # Observability
    "list_storage_paths": [_icon("hard-drive")],
    "get_storage_path": [_icon("hard-drive")],
    "list_saved_views": [_icon("eye")],
    "get_saved_view": [_icon("eye")],
    "list_share_links": [_icon("link")],
    "get_share_link": [_icon("link")],
    "list_tasks": [_icon("activity")],
    "get_task": [_icon("activity")],
    "wait_for_task": [_icon("hourglass")],
    "get_statistics": [_icon("bar-chart-3")],
    "get_remote_version": [_icon("cpu")],
    # Downloads
    "create_download_link": [_icon("link-2")],
}
