"""Tasks MCP resource."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register the tasks collection resource on *mcp*."""
    client = ctx.client

    @mcp.resource(uri="tasks://paperless", mime_type="application/json")
    async def tasks_resource() -> str:
        """Return all Paperless-NGX tasks as a JSON array."""
        task_list = await client.tasks.list()
        return json.dumps([t.model_dump() for t in task_list])
