"""Title registry: tool name → human-readable ``annotations.title``.

Title-aware MCP clients (notably VS Code, which honours only ``title`` and
``readOnlyHint`` among annotations) render this as the tool's label; without it
they fall back to the raw machine name.

This is a registry of its own rather than a key in
:data:`paperless_mcp.tools._annotations.ANNOTATION_REGISTRY` because the two
differ in kind: the four CRUD hints are *shared* — forty-nine tools map onto
five dicts — while a title is per-tool.  Folding titles into those dicts would
unshare all five to carry one string each.
:func:`paperless_mcp.tools._registry.register_tool` merges the two.

Most titles are the tool name in title case.  Where the name reads wrong on its
own, the title says what the tool does instead: ``get_remote_version`` asks
whether a newer Paperless exists rather than reporting the installed one, and
``get_document_metadata`` returns file facts (filename, checksums, MIME type)
rather than the catalogue metadata a reader might expect.

Names in the mapping match the registered MCP tool names exactly; keep it in
lock-step with :data:`paperless_mcp.tools._icons.ICON_REGISTRY` and
``ANNOTATION_REGISTRY``.
"""

from __future__ import annotations

TITLE_REGISTRY: dict[str, str] = {
    "create_document_download_link": "Create Document Download Link",
    "create_document_upload_link": "Create Document Upload Link",
    # Documents — reads
    "list_documents": "List Documents",
    "search_documents": "Search Documents",
    "get_document": "Get Document",
    "get_document_content": "Get Document Text",
    "get_document_thumbnail": "Get Document Thumbnail",
    "get_document_metadata": "Get Document File Details",
    "get_document_notes": "List Document Notes",
    "get_document_history": "Get Document Audit Log",
    "get_document_suggestions": "Suggest Tags, Correspondent and Type",
    # Documents — writes
    "update_document": "Update Document",
    "delete_document": "Delete Document Permanently",
    "upload_document": "Upload Document",
    "bulk_edit_documents": "Bulk Edit Documents",
    "add_document_note": "Add Document Note",
    "delete_document_note": "Delete Document Note",
    # Tags
    "list_tags": "List Tags",
    "get_tag": "Get Tag",
    "create_tag": "Create Tag",
    "update_tag": "Update Tag",
    "delete_tag": "Delete Tag",
    "bulk_edit_tags": "Bulk Add or Remove Tags",
    # Correspondents
    "list_correspondents": "List Correspondents",
    "get_correspondent": "Get Correspondent",
    "create_correspondent": "Create Correspondent",
    "update_correspondent": "Update Correspondent",
    "delete_correspondent": "Delete Correspondent",
    "bulk_edit_correspondents": "Bulk Edit Correspondents",
    # Document types
    "list_document_types": "List Document Types",
    "get_document_type": "Get Document Type",
    "create_document_type": "Create Document Type",
    "update_document_type": "Update Document Type",
    "delete_document_type": "Delete Document Type",
    "bulk_edit_document_types": "Bulk Edit Document Types",
    # Custom fields
    "list_custom_fields": "List Custom Fields",
    "get_custom_field": "Get Custom Field",
    "create_custom_field": "Create Custom Field",
    "update_custom_field": "Update Custom Field",
    "delete_custom_field": "Delete Custom Field",
    # Observability
    "list_storage_paths": "List Storage Paths",
    "get_storage_path": "Get Storage Path",
    "list_saved_views": "List Saved Views",
    "get_saved_view": "Get Saved View",
    "list_share_links": "List Share Links",
    "get_share_link": "Get Share Link",
    "list_tasks": "List Background Tasks",
    "get_task": "Get Background Task",
    "wait_for_task": "Wait for Task to Finish",
    "get_statistics": "Get Paperless Statistics",
    "get_remote_version": "Check for Paperless Updates",
}
