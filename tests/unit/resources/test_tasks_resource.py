from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from fastmcp import FastMCP

from paperless_mcp.resources import tasks as tasks_mod
from paperless_mcp.tools._context import ToolContext


def test_registers_tasks_uri() -> None:
    client = MagicMock()
    client.tasks.list = AsyncMock(return_value=[])
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=client, read_only=False, default_page_size=25, public_url=""
    )
    tasks_mod.register(mcp, ctx)
    uris = {str(r.uri) for r in asyncio.run(mcp.list_resources())}
    assert "tasks://paperless" in uris
