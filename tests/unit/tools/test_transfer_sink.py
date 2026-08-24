"""Tests for PaperlessTransferSink (pvl-core Transfer API domain hook)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from paperless_mcp.client._errors import PaperlessAPIError
from paperless_mcp.models.document import Document
from paperless_mcp.tools._transfer_sink import PaperlessTransferSink

_CREATED = datetime(2026, 1, 1, tzinfo=UTC)


def _document(original_file_name: str | None = "report.pdf") -> Document:
    return Document(
        id=982,
        title="Test document",
        created=_CREATED,
        original_file_name=original_file_name,
    )


def _mock_client(document: Document | None = None) -> Any:
    client = MagicMock()
    client.documents.get = AsyncMock(return_value=document or _document())
    client.documents.download = AsyncMock(
        return_value=(b"PDF-bytes", "application/pdf")
    )
    client.documents.get_preview = AsyncMock(
        return_value=(b"preview-bytes", "image/png")
    )
    return client


async def test_validate_bare_ref_defaults_to_original() -> None:
    sink = PaperlessTransferSink(_mock_client())
    handle = await sink.validate("982", "download")
    assert handle == "982:original"


async def test_validate_ref_with_variant() -> None:
    sink = PaperlessTransferSink(_mock_client())
    handle = await sink.validate("982:archived", "download")
    assert handle == "982:archived"


async def test_validate_rejects_unknown_variant() -> None:
    sink = PaperlessTransferSink(_mock_client())
    with pytest.raises(ValueError, match="variant"):
        await sink.validate("982:thumbnail", "download")


async def test_validate_rejects_non_numeric_ref() -> None:
    sink = PaperlessTransferSink(_mock_client())
    with pytest.raises(ValueError, match="document id"):
        await sink.validate("not-a-number", "download")


async def test_validate_rejects_missing_document() -> None:
    client = _mock_client()
    client.documents.get = AsyncMock(side_effect=PaperlessAPIError(404, "Not Found"))
    sink = PaperlessTransferSink(client)
    with pytest.raises(ValueError, match="982"):
        await sink.validate("982", "download")


async def test_validate_rejects_upload_kind() -> None:
    sink = PaperlessTransferSink(_mock_client())
    with pytest.raises(ValueError, match="upload"):
        await sink.validate("982", "upload")


async def test_read_original_variant() -> None:
    client = _mock_client()
    sink = PaperlessTransferSink(client)
    result = await sink.read("982:original")
    client.documents.download.assert_awaited_once_with(982, original=True)
    assert result.body == b"PDF-bytes"
    assert result.media_type == "application/pdf"
    assert result.filename == "report.pdf"


async def test_read_archived_variant() -> None:
    client = _mock_client()
    sink = PaperlessTransferSink(client)
    result = await sink.read("982:archived")
    client.documents.download.assert_awaited_once_with(982, original=False)
    assert result.filename == "report.pdf"


async def test_read_preview_variant_suffixes_filename() -> None:
    client = _mock_client()
    sink = PaperlessTransferSink(client)
    result = await sink.read("982:preview")
    client.documents.get_preview.assert_awaited_once_with(982)
    assert result.body == b"preview-bytes"
    assert result.media_type == "image/png"
    assert result.filename == "report-preview.pdf"


async def test_read_falls_back_to_generated_filename() -> None:
    client = _mock_client(document=_document(original_file_name=None))
    sink = PaperlessTransferSink(client)
    result = await sink.read("982:original")
    assert result.filename == "document-982"


async def test_write_is_not_supported() -> None:
    sink = PaperlessTransferSink(_mock_client())
    with pytest.raises(NotImplementedError):
        await sink.write("982:original", b"data")
