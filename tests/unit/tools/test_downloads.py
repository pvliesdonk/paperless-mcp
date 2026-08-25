"""Regression tests for removed download-link tools."""

from __future__ import annotations

import asyncio

from fastmcp import FastMCP

from paperless_mcp.tools import register_tools
from paperless_mcp.tools._context import ToolContext


def test_tool_registry_omits_download_link() -> None:
    """The unsupported download-link tool cannot be exposed to clients."""
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=object(),  # type: ignore[arg-type]
        read_only=False,
        default_page_size=25,
        public_url="",
    )
    register_tools(mcp, ctx)
    assert "create_download_link" not in {
        tool.name for tool in asyncio.run(mcp.list_tools())
    }
