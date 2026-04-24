"""Registration test for document tools."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from paperless_mcp.tools import documents as documents_mod
from paperless_mcp.tools._context import ToolContext


@pytest.fixture
def mock_client() -> Any:
    client = MagicMock()
    client.documents.list = AsyncMock()
    client.documents.search = AsyncMock()
    client.documents.get = AsyncMock()
    client.documents.get_content = AsyncMock()
    client.documents.get_thumbnail = AsyncMock()
    client.documents.get_metadata = AsyncMock()
    client.documents.get_notes = AsyncMock()
    client.documents.get_history = AsyncMock()
    client.documents.get_suggestions = AsyncMock()
    client.documents.update = AsyncMock()
    client.documents.delete = AsyncMock()
    client.documents.upload = AsyncMock()
    client.documents.bulk_edit = AsyncMock()
    client.documents.add_note = AsyncMock()
    client.documents.delete_note = AsyncMock()
    return client


def _registered_names(mcp: FastMCP) -> set[str]:
    tools = asyncio.run(mcp.list_tools())
    return {tool.name for tool in tools}


def test_read_only_registers_read_tools(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, read_only=True, default_page_size=25)
    documents_mod.register(mcp, ctx)
    names = _registered_names(mcp)
    assert "list_documents" in names
    assert "search_documents" in names
    assert "get_document" in names
    assert "get_document_content" in names
    assert "get_document_thumbnail" in names
    assert "get_document_metadata" in names
    assert "get_document_notes" in names
    assert "get_document_history" in names
    assert "get_document_suggestions" in names
    assert "update_document" not in names
    assert "delete_document" not in names
    assert "upload_document" not in names
    assert "bulk_edit_documents" not in names
    assert "add_document_note" not in names
    assert "delete_document_note" not in names


def test_read_write_registers_all(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, read_only=False, default_page_size=25)
    documents_mod.register(mcp, ctx)
    names = _registered_names(mcp)
    expected = {
        "list_documents",
        "search_documents",
        "get_document",
        "get_document_content",
        "get_document_thumbnail",
        "get_document_metadata",
        "get_document_notes",
        "get_document_history",
        "get_document_suggestions",
        "update_document",
        "delete_document",
        "upload_document",
        "bulk_edit_documents",
        "add_document_note",
        "delete_document_note",
    }
    assert expected.issubset(names)


def test_all_tools_have_icons(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, read_only=False, default_page_size=25)
    documents_mod.register(mcp, ctx)
    tools = asyncio.run(mcp.list_tools())
    for tool in tools:
        assert tool.icons, f"tool {tool.name} missing icons"
