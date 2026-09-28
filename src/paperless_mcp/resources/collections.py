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
        """The Paperless URL, public URL and default page size this server uses."""
        snapshot = {
            "paperless_url": client.http.base_url,
            "paperless_public_url": ctx.public_url,
            "default_page_size": ctx.default_page_size,
        }
        return json.dumps(snapshot)

    @mcp.resource(uri="stats://paperless", mime_type="application/json")
    async def stats_resource() -> str:
        """Archive-wide counts: documents, inbox, tags, correspondents and types."""
        stats = await client.system.statistics()
        return stats.model_dump_json()

    @mcp.resource(uri="remote-version://paperless", mime_type="application/json")
    async def remote_version_resource() -> str:
        """The newest release of Paperless-NGX, not the version installed here, and whether it is newer."""
        rv = await client.system.remote_version()
        return rv.model_dump_json()

    @mcp.resource(uri="tags://paperless", mime_type="application/json")
    async def tags_resource() -> str:
        """Every tag, with its id, name and colour."""
        items = [item async for item in client.http.paginate("/api/tags/")]
        return json.dumps(items)

    @mcp.resource(uri="correspondents://paperless", mime_type="application/json")
    async def correspondents_resource() -> str:
        """Every correspondent, with its id, name and the date of its newest document."""
        items = [
            item
            async for item in client.http.paginate(
                "/api/correspondents/", params={"last_correspondence": "true"}
            )
        ]
        return json.dumps(items)

    @mcp.resource(uri="document-types://paperless", mime_type="application/json")
    async def document_types_resource() -> str:
        """Every document type, with its id and name."""
        items = [item async for item in client.http.paginate("/api/document_types/")]
        return json.dumps(items)

    @mcp.resource(uri="custom-fields://paperless", mime_type="application/json")
    async def custom_fields_resource() -> str:
        """Every custom field definition, with its id, name and type."""
        items = [item async for item in client.http.paginate("/api/custom_fields/")]
        return json.dumps(items)

    @mcp.resource(uri="storage-paths://paperless", mime_type="application/json")
    async def storage_paths_resource() -> str:
        """Every storage path, with its id, name and path template."""
        items = [item async for item in client.http.paginate("/api/storage_paths/")]
        return json.dumps(items)

    @mcp.resource(uri="saved-views://paperless", mime_type="application/json")
    async def saved_views_resource() -> str:
        """Every saved view, with its id, name and filter rules."""
        items = [item async for item in client.http.paginate("/api/saved_views/")]
        return json.dumps(items)
