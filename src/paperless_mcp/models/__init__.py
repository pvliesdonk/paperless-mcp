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
from paperless_mcp.models.document_type import DocumentType, DocumentTypeCreate, DocumentTypePatch
from paperless_mcp.models.custom_field import CustomField, CustomFieldCreate, CustomFieldDataType, CustomFieldPatch
from paperless_mcp.models.storage_path import StoragePath
from paperless_mcp.models.saved_view import SavedView
from paperless_mcp.models.share_link import ShareLink, ShareLinkFileVersion
from paperless_mcp.models.task import Task, TaskStatus
from paperless_mcp.models.system import RemoteVersion, Statistics
__all__ = [
    "BulkEditOperation", "BulkEditResult", "DownloadLink", "ListParams", "Paginated", "UploadTaskAcknowledgement",
    "CustomFieldInstance", "Document", "DocumentHistoryEntry", "DocumentMetadata", "DocumentNote", "DocumentPatch", "DocumentSuggestions",
    "Tag", "TagCreate", "TagPatch",
    "Correspondent", "CorrespondentCreate", "CorrespondentPatch",
    "DocumentType", "DocumentTypeCreate", "DocumentTypePatch",
    "CustomField", "CustomFieldCreate", "CustomFieldDataType", "CustomFieldPatch",
    "StoragePath", "SavedView", "ShareLink", "ShareLinkFileVersion",
    "Task", "TaskStatus",
    "RemoteVersion", "Statistics",
]
