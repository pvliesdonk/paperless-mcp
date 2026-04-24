from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from fastmcp import FastMCP

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
        "get_preview",
        "download",
        "get_content",
    ):
        setattr(client.documents, meth, AsyncMock())
    return client


def _templates(mcp: FastMCP) -> set[str]:
    return {t.uri_template for t in asyncio.run(mcp.list_resource_templates())}


def test_registers_templated_uris() -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=_mock_client(), read_only=False, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    templates = _templates(mcp)
    expected = {
        "paperless://documents/{document_id}",
        "paperless://documents/{document_id}/content",
        "paperless://documents/{document_id}/metadata",
        "paperless://documents/{document_id}/notes",
        "paperless://documents/{document_id}/history",
        "paperless://documents/{document_id}/thumbnail",
        "paperless://documents/{document_id}/preview",
        "paperless://documents/{document_id}/download",
    }
    assert expected.issubset(templates)
