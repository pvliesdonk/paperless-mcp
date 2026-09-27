"""Per-document templated MCP resource URIs."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from paperless_mcp._content import slice_content
from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register per-document templated MCP resources on *mcp*."""
    client = ctx.client

    @mcp.resource(
        uri="paperless://documents/{document_id}", mime_type="application/json"
    )
    async def document_resource(document_id: int) -> str:
        """A document's metadata, without its text."""
        doc = await client.documents.get(document_id)
        doc.content = None
        return doc.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/content", mime_type="text/plain"
    )
    async def document_content_resource(document_id: int) -> str:
        """The first part of a document's text."""
        text = await client.documents.get_content(document_id)
        return slice_content(text)

    @mcp.resource(
        uri="paperless://documents/{document_id}/metadata",
        mime_type="application/json",
    )
    async def document_metadata_resource(document_id: int) -> str:
        """A document's file details: names, sizes, checksums and MIME type."""
        meta = await client.documents.get_metadata(document_id)
        return meta.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/notes", mime_type="application/json"
    )
    async def document_notes_resource(document_id: int) -> str:
        """The notes on a document."""
        notes = await client.documents.get_notes(document_id)
        return json.dumps([n.model_dump() for n in notes])

    @mcp.resource(
        uri="paperless://documents/{document_id}/history", mime_type="application/json"
    )
    async def document_history_resource(document_id: int) -> str:
        """The change history of a document."""
        entries = await client.documents.get_history(document_id)
        return json.dumps([e.model_dump() for e in entries])

    @mcp.resource(
        uri="paperless://documents/{document_id}/thumbnail", mime_type="image/png"
    )
    async def document_thumbnail_resource(document_id: int) -> bytes:
        """A small image of a document's first page."""
        data, _ = await client.documents.get_thumbnail(document_id)
        return data
