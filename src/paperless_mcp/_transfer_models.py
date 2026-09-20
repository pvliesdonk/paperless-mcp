"""Validated document transfer handles and Markdown rendering.

External contracts: ``docs/design/reference/core-transfer-links.md``.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from paperless_mcp.models.document import Document

DocumentVariant = Literal["original", "archive", "preview", "content"]
PositiveId = Annotated[int, Field(gt=0)]


class UploadMetadata(BaseModel):
    """Optional Paperless metadata, supplied explicitly when minting a link."""

    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    correspondent: PositiveId | None = None
    document_type: PositiveId | None = None
    tags: list[PositiveId] | None = None
    created: str | None = None
    archive_serial_number: str | int | None = None
    custom_fields: list[PositiveId] | None = None


class UploadReference(BaseModel):
    """Caller-supplied filename and metadata for a new document."""

    model_config = ConfigDict(extra="forbid")
    filename: str = Field(min_length=1, max_length=255)
    metadata: UploadMetadata = Field(default_factory=UploadMetadata)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        """Require a plain filename without directories or control characters."""
        if value in {".", ".."} or any(
            c in "/\\" or not c.isprintable() for c in value
        ):
            raise ValueError("filename must be a plain filename without a path")
        return value


class UploadHandle(UploadReference):
    """Persisted destination with server-owned identity and receipt retention."""

    operation_id: str
    expires_at: float = Field(gt=0, allow_inf_nan=False)


class DownloadHandle(BaseModel):
    """A document and the file representation to retrieve at redemption."""

    model_config = ConfigDict(extra="forbid")
    document_id: PositiveId
    variant: DocumentVariant = "original"


def render_markdown(document: Document) -> bytes:
    """Render full OCR text with JSON-quoted YAML front matter as UTF-8.

    The OCR body is preserved verbatim; no headings or layout are inferred.
    Related objects are IDs, matching Paperless's document representation.

    Args:
        document: The full Paperless document, including OCR content.

    Returns:
        Markdown bytes containing a small metadata block and the original text.
    """
    metadata = document.model_dump(
        mode="json",
        include={"id", "title", "created", "correspondent", "document_type", "tags"},
    )
    front_matter = "\n".join(
        f"{key}: {json.dumps(value)}" for key, value in metadata.items()
    )
    return f"---\n{front_matter}\n---\n\n{document.content or ''}".encode()
