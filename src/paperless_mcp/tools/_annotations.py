"""MCP tool annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint).

Every tool that talks to Paperless is ``openWorldHint=True`` — it interacts with
an external system.  The other hints encode CRUD semantics and guide clients
on when to prompt for confirmation / cache results.

Keep this registry in lock-step with :data:`paperless_mcp.tools._icons.ICON_REGISTRY`;
:func:`paperless_mcp.tools._registry.register_tool` raises ``KeyError`` on mismatch.
"""

from __future__ import annotations

_READ: dict[str, bool] = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
_CREATE: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
_UPDATE: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
_DELETE: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}
_BULK_EDIT: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}

ANNOTATION_REGISTRY: dict[str, dict[str, bool]] = {
    # Documents — reads
    "list_documents": _READ,
    "search_documents": _READ,
    "get_document": _READ,
    "get_document_content": _READ,
    "get_document_thumbnail": _READ,
    "get_document_metadata": _READ,
    "get_document_notes": _READ,
    "get_document_history": _READ,
    "get_document_suggestions": _READ,
    # Documents — writes
    "update_document": _UPDATE,
    "delete_document": _DELETE,
    "upload_document": _CREATE,
    "bulk_edit_documents": _BULK_EDIT,
    "add_document_note": _CREATE,
    "delete_document_note": _DELETE,
    # Tags
    "list_tags": _READ,
    "get_tag": _READ,
    "create_tag": _CREATE,
    "update_tag": _UPDATE,
    "delete_tag": _DELETE,
    "bulk_edit_tags": _BULK_EDIT,
    # Correspondents
    "list_correspondents": _READ,
    "get_correspondent": _READ,
    "create_correspondent": _CREATE,
    "update_correspondent": _UPDATE,
    "delete_correspondent": _DELETE,
    "bulk_edit_correspondents": _BULK_EDIT,
    # Document types
    "list_document_types": _READ,
    "get_document_type": _READ,
    "create_document_type": _CREATE,
    "update_document_type": _UPDATE,
    "delete_document_type": _DELETE,
    "bulk_edit_document_types": _BULK_EDIT,
    # Custom fields
    "list_custom_fields": _READ,
    "get_custom_field": _READ,
    "create_custom_field": _CREATE,
    "update_custom_field": _UPDATE,
    "delete_custom_field": _DELETE,
    # Observability
    "list_storage_paths": _READ,
    "get_storage_path": _READ,
    "list_saved_views": _READ,
    "get_saved_view": _READ,
    "list_share_links": _READ,
    "get_share_link": _READ,
    "list_tasks": _READ,
    "get_task": _READ,
    "wait_for_task": _READ,
    "get_statistics": _READ,
    "get_remote_version": _READ,
    # Downloads — mints a new URL each call but kept read-only so it's
    # available in read-only mode (observe + share).
    "create_download_link": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
}
