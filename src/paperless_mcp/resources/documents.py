"""Per-document templated MCP resource URIs."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register per-document templated MCP resources on *mcp*."""
    client = ctx.client

    @mcp.resource(
        uri="paperless://documents/{document_id}", mime_type="application/json"
    )
    async def document_resource(document_id: int) -> str:
        """Return a single document by ID as JSON."""
        doc = await client.documents.get(document_id)
        return doc.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/content", mime_type="text/plain"
    )
    async def document_content_resource(document_id: int) -> str:
        """Return the plain-text content of a document."""
        return await client.documents.get_content(document_id)

    @mcp.resource(
        uri="paperless://documents/{document_id}/metadata",
        mime_type="application/json",
    )
    async def document_metadata_resource(document_id: int) -> str:
        """Return document metadata as JSON."""
        meta = await client.documents.get_metadata(document_id)
        return meta.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/notes", mime_type="application/json"
    )
    async def document_notes_resource(document_id: int) -> str:
        """Return all notes for a document as a JSON array."""
        notes = await client.documents.get_notes(document_id)
        return json.dumps([n.model_dump() for n in notes])

    @mcp.resource(
        uri="paperless://documents/{document_id}/history", mime_type="application/json"
    )
    async def document_history_resource(document_id: int) -> str:
        """Return audit-log history for a document as a JSON array."""
        entries = await client.documents.get_history(document_id)
        return json.dumps([e.model_dump() for e in entries])

    @mcp.resource(
        uri="paperless://documents/{document_id}/thumbnail", mime_type="image/png"
    )
    async def document_thumbnail_resource(document_id: int) -> bytes:
        """Return the thumbnail image bytes for a document."""
        data, _ = await client.documents.get_thumbnail(document_id)
        return data

    @mcp.resource(
        uri="paperless://documents/{document_id}/preview", mime_type="application/pdf"
    )
    async def document_preview_resource(document_id: int) -> bytes:
        """Return the PDF preview bytes for a document."""
        data, _ = await client.documents.get_preview(document_id)
        return data

    @mcp.resource(
        uri="paperless://documents/{document_id}/download",
        mime_type="application/octet-stream",
    )
    async def document_download_resource(document_id: int) -> bytes:
        """Return the original file bytes for a document."""
        data, _ = await client.documents.download(document_id)
        return data
