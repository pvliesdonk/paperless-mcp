from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastmcp import Client, FastMCP
from mcp.types import TextResourceContents

from paperless_mcp._content import CONTENT_CHAR_CAP
from paperless_mcp.models.document import Document
from paperless_mcp.resources import documents as documents_mod
from paperless_mcp.tools._context import ToolContext


def _mock_client() -> Any:
    client = MagicMock()
    for meth in (
        "get",
        "get_metadata",
        "get_notes",
        "get_history",
        "get_thumbnail",
        "get_content",
    ):
        setattr(client.documents, meth, AsyncMock())
    return client


def _templates(mcp: FastMCP) -> set[str]:
    return {t.uri_template for t in asyncio.run(mcp.list_resource_templates())}


def test_registers_templated_uris() -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), default_page_size=25, public_url="")
    documents_mod.register(mcp, ctx)
    templates = _templates(mcp)
    expected = {
        "paperless://documents/{document_id}",
        "paperless://documents/{document_id}/content",
        "paperless://documents/{document_id}/metadata",
        "paperless://documents/{document_id}/notes",
        "paperless://documents/{document_id}/history",
        "paperless://documents/{document_id}/thumbnail",
    }
    assert templates == expected


async def test_document_resource_strips_ocr_content() -> None:
    upstream = _mock_client()
    upstream.documents.get.return_value = Document(
        id=42,
        title="Bounded",
        created=datetime(2026, 1, 1, tzinfo=UTC),
        content="A" * (CONTENT_CHAR_CAP + 1),
    )
    mcp = FastMCP("test")
    documents_mod.register(
        mcp, ToolContext(client=upstream, default_page_size=25, public_url="")
    )

    async with Client(mcp) as client:
        contents = await client.read_resource("paperless://documents/42")

    assert len(contents) == 1
    content = contents[0]
    assert isinstance(content, TextResourceContents)
    assert json.loads(content.text)["content"] is None


async def test_document_content_resource_returns_bounded_preview() -> None:
    upstream = _mock_client()
    text = "A" * (CONTENT_CHAR_CAP + 1)
    upstream.documents.get_content.return_value = text
    mcp = FastMCP("test")
    documents_mod.register(
        mcp, ToolContext(client=upstream, default_page_size=25, public_url="")
    )

    async with Client(mcp) as client:
        contents = await client.read_resource("paperless://documents/42/content")

    assert len(contents) == 1
    content = contents[0]
    assert isinstance(content, TextResourceContents)
    marker, _, body = content.text.partition("\n\n")
    assert body == text[:CONTENT_CHAR_CAP]
    assert f"offset={CONTENT_CHAR_CAP}" in marker
    assert "create_download_link" in marker
