"""Registration test for document tools."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError

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


def test_read_write_registers_all(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    documents_mod.register(mcp, ctx)
    tools = asyncio.run(mcp.list_tools())
    for tool in tools:
        assert tool.icons, f"tool {tool.name} missing icons"


def test_list_and_search_expose_include_content(mock_client: Any) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    documents_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    for name in ("get_document", "update_document"):
        schema = tools[name].parameters
        assert "include_content" in schema["properties"], name
        assert schema["properties"]["include_content"].get("default") is False


@pytest.mark.asyncio
async def test_get_document_strips_content_by_default(mock_client: Any) -> None:
    mcp = FastMCP("t")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
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


def _content_mcp(mock_client: Any) -> FastMCP:
    """Register document tools against *mock_client* for content tests."""
    mcp = FastMCP("t")
    ctx = ToolContext(client=mock_client, default_page_size=25, public_url="")
    documents_mod.register(mcp, ctx)
    return mcp


def test_get_document_content_exposes_cap_and_offset(mock_client: Any) -> None:
    tools = {t.name: t for t in asyncio.run(_content_mcp(mock_client).list_tools())}
    props = tools["get_document_content"].parameters["properties"]
    assert props["max_chars"]["default"] == documents_mod.CONTENT_CHAR_CAP
    assert props["offset"]["default"] == 0


@pytest.mark.asyncio
async def test_get_document_content_caps_by_default(mock_client: Any) -> None:
    """The cap applies when the caller omits it, which is the flooding case."""
    text = "A" * 250_000
    mock_client.documents.get_content.return_value = text

    async with Client(_content_mcp(mock_client)) as c:
        result = await c.call_tool("get_document_content", {"document_id": 1})

    out = result.data
    marker, _, body = out.partition("\n\n")
    assert body == text[: documents_mod.CONTENT_CHAR_CAP]
    assert "of 250,000" in marker
    assert f"offset={documents_mod.CONTENT_CHAR_CAP}" in marker


@pytest.mark.asyncio
async def test_get_document_content_returns_short_text_unchanged(
    mock_client: Any,
) -> None:
    """Text under the cap comes back byte-identical, with no marker."""
    mock_client.documents.get_content.return_value = "short OCR text"

    async with Client(_content_mcp(mock_client)) as c:
        result = await c.call_tool("get_document_content", {"document_id": 1})

    assert result.data == "short OCR text"


@pytest.mark.asyncio
async def test_get_document_content_offset_continues(mock_client: Any) -> None:
    text = "A" * 60_000 + "B" * 60_000
    mock_client.documents.get_content.return_value = text

    async with Client(_content_mcp(mock_client)) as c:
        result = await c.call_tool(
            "get_document_content",
            {"document_id": 1, "max_chars": 60_000, "offset": 60_000},
        )

    marker, _, body = result.data.partition("\n\n")
    assert body == "B" * 60_000
    assert "final section" in marker


@pytest.mark.asyncio
async def test_get_document_content_offset_past_end(mock_client: Any) -> None:
    mock_client.documents.get_content.return_value = "A" * 100

    async with Client(_content_mcp(mock_client)) as c:
        result = await c.call_tool(
            "get_document_content", {"document_id": 1, "offset": 5_000}
        )

    assert "past the end" in result.data
    assert "100 chars" in result.data


@pytest.mark.asyncio
async def test_get_document_content_rejects_non_advancing_bounds(
    mock_client: Any,
) -> None:
    """A zero or negative cap would hand back a marker that never advances.

    The offset a truncation marker names is ``offset + max_chars``, so a cap
    of zero would advertise the offset the caller just used and invite a model
    to loop on it forever.  Keep the bounds enforced at the schema.
    """
    mock_client.documents.get_content.return_value = "A" * 100

    async with Client(_content_mcp(mock_client)) as c:
        for args in (
            {"document_id": 1, "max_chars": 0},
            {"document_id": 1, "max_chars": -5},
            {"document_id": 1, "offset": -1},
        ):
            with pytest.raises(ToolError):
                await c.call_tool("get_document_content", args)


@pytest.mark.asyncio
async def test_get_document_content_unlimited_when_max_chars_none(
    mock_client: Any,
) -> None:
    text = "A" * 250_000
    mock_client.documents.get_content.return_value = text

    async with Client(_content_mcp(mock_client)) as c:
        result = await c.call_tool(
            "get_document_content", {"document_id": 1, "max_chars": None}
        )

    assert result.data == text
