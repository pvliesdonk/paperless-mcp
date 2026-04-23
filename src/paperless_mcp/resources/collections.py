"""Fixed, collection-level MCP resource URIs."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    client = ctx.client

    @mcp.resource(uri="config://paperless", mime_type="application/json")
    async def config_resource() -> str:
        snapshot = {
            "paperless_url": str(client.http.base_url),
            "read_only": ctx.read_only,
            "default_page_size": ctx.default_page_size,
        }
        return json.dumps(snapshot)

    @mcp.resource(uri="stats://paperless", mime_type="application/json")
    async def stats_resource() -> str:
        stats = await client.system.statistics()
        return stats.model_dump_json()

    @mcp.resource(uri="remote-version://paperless", mime_type="application/json")
    async def remote_version_resource() -> str:
        rv = await client.system.remote_version()
        return rv.model_dump_json()

    @mcp.resource(uri="tags://paperless", mime_type="application/json")
    async def tags_resource() -> str:
        body = await client.tags.list(page_size=100)
        return body.model_dump_json()

    @mcp.resource(uri="correspondents://paperless", mime_type="application/json")
    async def correspondents_resource() -> str:
        body = await client.correspondents.list(page_size=100)
        return body.model_dump_json()

    @mcp.resource(uri="document-types://paperless", mime_type="application/json")
    async def document_types_resource() -> str:
        body = await client.document_types.list(page_size=100)
        return body.model_dump_json()

    @mcp.resource(uri="custom-fields://paperless", mime_type="application/json")
    async def custom_fields_resource() -> str:
        body = await client.custom_fields.list(page_size=100)
        return body.model_dump_json()

    @mcp.resource(uri="storage-paths://paperless", mime_type="application/json")
    async def storage_paths_resource() -> str:
        body = await client.storage_paths.list(page_size=100)
        return body.model_dump_json()

    @mcp.resource(uri="saved-views://paperless", mime_type="application/json")
    async def saved_views_resource() -> str:
        body = await client.saved_views.list(page_size=100)
        return body.model_dump_json()
