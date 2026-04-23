"""Pydantic models for Paperless-NGX resources."""
from __future__ import annotations
from paperless_mcp.models.common import (
    BulkEditOperation, BulkEditResult, DownloadLink, ListParams, Paginated, UploadTaskAcknowledgement,
)
from paperless_mcp.models.document import (
    CustomFieldInstance, Document, DocumentHistoryEntry, DocumentMetadata, DocumentNote, DocumentPatch, DocumentSuggestions,
)
from paperless_mcp.models.tag import Tag, TagCreate, TagPatch
from paperless_mcp.models.correspondent import Correspondent, CorrespondentCreate, CorrespondentPatch
__all__ = [
    "BulkEditOperation", "BulkEditResult", "DownloadLink", "ListParams", "Paginated", "UploadTaskAcknowledgement",
    "CustomFieldInstance", "Document", "DocumentHistoryEntry", "DocumentMetadata", "DocumentNote", "DocumentPatch", "DocumentSuggestions",
    "Tag", "TagCreate", "TagPatch",
    "Correspondent", "CorrespondentCreate", "CorrespondentPatch",
]
