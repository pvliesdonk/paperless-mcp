"""Registration test for document tools."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.document import Document
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
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
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
    ctx = ToolContext(
        client=mock_client, read_only=False, default_page_size=25, public_url=""
    )
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
    ctx = ToolContext(
        client=mock_client, read_only=False, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    tools = asyncio.run(mcp.list_tools())
    for tool in tools:
        assert tool.icons, f"tool {tool.name} missing icons"


def test_list_and_search_expose_include_content(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    for name in ("list_documents", "search_documents"):
        schema = tools[name].parameters
        assert "include_content" in schema["properties"]
        assert schema["properties"]["include_content"].get("default") is False


@pytest.mark.asyncio
async def test_get_document_populates_web_url(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client,
        read_only=True,
        default_page_size=25,
        public_url="https://docs.example.com",
    )
    documents_mod.register(mcp, ctx)

    mock_client.documents.get.return_value = Document(
        id=42, title="X", created=datetime(2026, 1, 1, tzinfo=UTC)
    )

    async with Client(mcp) as c:
        result = await c.call_tool("get_document", {"document_id": 42})

    data = result.structured_content
    assert data is not None
    assert data["web_url"] == "https://docs.example.com/documents/42/"


def test_get_document_and_update_document_expose_include_content(
    mock_client: Any,
) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=mock_client, read_only=False, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    for name in ("get_document", "update_document"):
        schema = tools[name].parameters
        assert "include_content" in schema["properties"], name
        assert schema["properties"]["include_content"].get("default") is False


@pytest.mark.asyncio
async def test_get_document_strips_content_by_default(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.get.return_value = Document(
        id=42,
        title="X",
        created=datetime(2026, 1, 1, tzinfo=UTC),
        content="A" * 50_000,
    )

    async with Client(mcp) as c:
        result = await c.call_tool("get_document", {"document_id": 42})

    data = result.structured_content
    assert data is not None
    assert data["content"] is None


@pytest.mark.asyncio
async def test_get_document_keeps_content_when_include_content_true(
    mock_client: Any,
) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client, read_only=True, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.get.return_value = Document(
        id=42,
        title="X",
        created=datetime(2026, 1, 1, tzinfo=UTC),
        content="OCR text",
    )

    async with Client(mcp) as c:
        result = await c.call_tool(
            "get_document", {"document_id": 42, "include_content": True}
        )

    data = result.structured_content
    assert data is not None
    assert data["content"] == "OCR text"


@pytest.mark.asyncio
async def test_update_document_strips_content_by_default(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client, read_only=False, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.update.return_value = Document(
        id=42,
        title="X",
        created=datetime(2026, 1, 1, tzinfo=UTC),
        content="A" * 50_000,
    )

    async with Client(mcp) as c:
        result = await c.call_tool(
            "update_document", {"document_id": 42, "patch": {"title": "Y"}}
        )

    data = result.structured_content
    assert data is not None
    assert data["content"] is None


@pytest.mark.asyncio
async def test_update_document_keeps_content_when_include_content_true(
    mock_client: Any,
) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client, read_only=False, default_page_size=25, public_url=""
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.update.return_value = Document(
        id=42,
        title="X",
        created=datetime(2026, 1, 1, tzinfo=UTC),
        content="OCR text",
    )

    async with Client(mcp) as c:
        result = await c.call_tool(
            "update_document",
            {"document_id": 42, "patch": {"title": "Y"}, "include_content": True},
        )

    data = result.structured_content
    assert data is not None
    assert data["content"] == "OCR text"


@pytest.mark.asyncio
async def test_list_documents_populates_web_url(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client,
        read_only=True,
        default_page_size=25,
        public_url="https://docs.example.com",
    )
    documents_mod.register(mcp, ctx)
    page = Paginated[Document].model_validate(
        {
            "count": 1,
            "next": None,
            "previous": None,
            "all": [42],
            "results": [{"id": 42, "title": "X", "created": "2026-01-01T00:00:00Z"}],
        }
    )
    mock_client.documents.list.return_value = page

    async with Client(mcp) as c:
        result = await c.call_tool("list_documents", {})

    data = result.structured_content
    assert data is not None
    assert data["results"][0]["web_url"] == "https://docs.example.com/documents/42/"


@pytest.mark.asyncio
async def test_search_documents_populates_web_url(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client,
        read_only=True,
        default_page_size=25,
        public_url="https://docs.example.com",
    )
    documents_mod.register(mcp, ctx)
    page = Paginated[Document].model_validate(
        {
            "count": 1,
            "next": None,
            "previous": None,
            "all": [99],
            "results": [{"id": 99, "title": "Y", "created": "2026-01-01T00:00:00Z"}],
        }
    )
    mock_client.documents.search.return_value = page

    async with Client(mcp) as c:
        result = await c.call_tool("search_documents", {"query": "foo"})

    data = result.structured_content
    assert data is not None
    assert data["results"][0]["web_url"] == "https://docs.example.com/documents/99/"


@pytest.mark.asyncio
async def test_update_document_populates_web_url(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client,
        read_only=False,
        default_page_size=25,
        public_url="https://docs.example.com",
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.update.return_value = Document(
        id=42, title="X", created=datetime(2026, 1, 1, tzinfo=UTC)
    )

    async with Client(mcp) as c:
        result = await c.call_tool(
            "update_document", {"document_id": 42, "patch": {"title": "Y"}}
        )

    data = result.structured_content
    assert data is not None
    assert data["web_url"] == "https://docs.example.com/documents/42/"


@pytest.mark.asyncio
async def test_web_url_none_when_public_url_empty(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(
        client=mock_client,
        read_only=True,
        default_page_size=25,
        public_url="",
    )
    documents_mod.register(mcp, ctx)
    mock_client.documents.get.return_value = Document(
        id=42, title="X", created=datetime(2026, 1, 1, tzinfo=UTC)
    )

    async with Client(mcp) as c:
        result = await c.call_tool("get_document", {"document_id": 42})

    data = result.structured_content
    assert data is not None
    assert data.get("web_url") is None
