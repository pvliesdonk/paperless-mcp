"""Fixed, collection-level MCP resource URIs."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register fixed collection-level MCP resources on *mcp*."""
    client = ctx.client

    @mcp.resource(uri="config://paperless", mime_type="application/json")
    async def config_resource() -> str:
        """Return server configuration as JSON."""
        snapshot = {
            "paperless_url": client.http.base_url,
            "read_only": ctx.read_only,
            "default_page_size": ctx.default_page_size,
        }
        return json.dumps(snapshot)

    @mcp.resource(uri="stats://paperless", mime_type="application/json")
    async def stats_resource() -> str:
        """Return Paperless-NGX document statistics as JSON."""
        stats = await client.system.statistics()
        return stats.model_dump_json()

    @mcp.resource(uri="remote-version://paperless", mime_type="application/json")
    async def remote_version_resource() -> str:
        """Return the remote Paperless-NGX version as JSON."""
        rv = await client.system.remote_version()
        return rv.model_dump_json()

    @mcp.resource(uri="tags://paperless", mime_type="application/json")
    async def tags_resource() -> str:
        """Return all tags as a paginated JSON object."""
        body = await client.tags.list(page_size=ctx.default_page_size)
        return body.model_dump_json()

    @mcp.resource(uri="correspondents://paperless", mime_type="application/json")
    async def correspondents_resource() -> str:
        """Return all correspondents as a paginated JSON object."""
        body = await client.correspondents.list(page_size=ctx.default_page_size)
        return body.model_dump_json()

    @mcp.resource(uri="document-types://paperless", mime_type="application/json")
    async def document_types_resource() -> str:
        """Return all document types as a paginated JSON object."""
        body = await client.document_types.list(page_size=ctx.default_page_size)
        return body.model_dump_json()

    @mcp.resource(uri="custom-fields://paperless", mime_type="application/json")
    async def custom_fields_resource() -> str:
        """Return all custom fields as a paginated JSON object."""
        body = await client.custom_fields.list(page_size=ctx.default_page_size)
        return body.model_dump_json()

    @mcp.resource(uri="storage-paths://paperless", mime_type="application/json")
    async def storage_paths_resource() -> str:
        """Return all storage paths as a paginated JSON object."""
        body = await client.storage_paths.list(page_size=ctx.default_page_size)
        return body.model_dump_json()

    @mcp.resource(uri="saved-views://paperless", mime_type="application/json")
    async def saved_views_resource() -> str:
        """Return all saved views as a paginated JSON object."""
        body = await client.saved_views.list(page_size=ctx.default_page_size)
        return body.model_dump_json()
