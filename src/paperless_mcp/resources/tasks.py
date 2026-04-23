"""Tasks MCP resource."""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    client = ctx.client

    @mcp.resource(uri="tasks://paperless", mime_type="application/json")
    async def tasks_resource() -> str:
        task_list = await client.tasks.list()
        return "[" + ",".join(t.model_dump_json() for t in task_list) + "]"
