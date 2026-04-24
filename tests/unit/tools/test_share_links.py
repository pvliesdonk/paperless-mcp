"""Tool-layer tests for share-link tools with share_url."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import Client, FastMCP

from paperless_mcp.models.common import Paginated
from paperless_mcp.models.share_link import ShareLink, ShareLinkFileVersion
from paperless_mcp.tools import share_links as sl_mod
from paperless_mcp.tools._context import ToolContext


def _link() -> ShareLink:
    return ShareLink(
        id=1,
        created=datetime(2026, 1, 1, tzinfo=UTC),
        slug="abc123",
        document=42,
        file_version=ShareLinkFileVersion.ARCHIVE,
    )


@pytest.mark.asyncio
async def test_get_share_link_populates_share_url() -> None:
    client = MagicMock()
    client.share_links.get = AsyncMock(return_value=_link())
    mcp = FastMCP("t")
    sl_mod.register(
        mcp,
        ToolContext(
            client=client,
            read_only=True,
            default_page_size=25,
            public_url="https://docs.example.com",
        ),
    )
    async with Client(mcp) as c:
        result = await c.call_tool("get_share_link", {"share_link_id": 1})
    data = result.structured_content
    assert data is not None
    assert data["share_url"] == "https://docs.example.com/share/abc123"


@pytest.mark.asyncio
async def test_list_share_links_populates_share_url() -> None:
    client = MagicMock()
    client.share_links.list = AsyncMock(
        return_value=Paginated[ShareLink].model_validate(
            {
                "count": 1,
                "next": None,
                "previous": None,
                "all": [1],
                "results": [
                    {
                        "id": 1,
                        "created": "2026-01-01T00:00:00Z",
                        "slug": "abc123",
                        "document": 42,
                        "file_version": "archive",
                    }
                ],
            }
        )
    )
    mcp = FastMCP("t")
    sl_mod.register(
        mcp,
        ToolContext(
            client=client,
            read_only=True,
            default_page_size=25,
            public_url="https://docs.example.com",
        ),
    )
    async with Client(mcp) as c:
        result = await c.call_tool("list_share_links", {})
    data = result.structured_content
    assert data is not None
    assert data["results"][0]["share_url"] == "https://docs.example.com/share/abc123"


@pytest.mark.asyncio
async def test_get_share_url_is_none_when_public_url_empty() -> None:
    client = MagicMock()
    client.share_links.get = AsyncMock(return_value=_link())
    mcp = FastMCP("t")
    sl_mod.register(
        mcp,
        ToolContext(
            client=client,
            read_only=True,
            default_page_size=25,
            public_url="",
        ),
    )
    async with Client(mcp) as c:
        result = await c.call_tool("get_share_link", {"share_link_id": 1})
    data = result.structured_content
    assert data is not None
    assert data.get("share_url") is None


@pytest.mark.asyncio
async def test_list_share_url_is_none_when_public_url_empty() -> None:
    client = MagicMock()
    client.share_links.list = AsyncMock(
        return_value=Paginated[ShareLink].model_validate(
            {
                "count": 1,
                "next": None,
                "previous": None,
                "all": [1],
                "results": [
                    {
                        "id": 1,
                        "created": "2026-01-01T00:00:00Z",
                        "slug": "abc123",
                        "document": 42,
                        "file_version": "archive",
                    }
                ],
            }
        )
    )
    mcp = FastMCP("t")
    sl_mod.register(
        mcp,
        ToolContext(
            client=client,
            read_only=True,
            default_page_size=25,
            public_url="",
        ),
    )
    async with Client(mcp) as c:
        result = await c.call_tool("list_share_links", {})
    data = result.structured_content
    assert data is not None
    assert data["results"][0].get("share_url") is None
