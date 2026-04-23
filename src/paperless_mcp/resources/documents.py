"""Per-document templated MCP resource URIs."""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp.tools._context import ToolContext


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    client = ctx.client

    @mcp.resource(
        uri="paperless://documents/{document_id}", mime_type="application/json"
    )
    async def document_resource(document_id: int) -> str:
        doc = await client.documents.get(document_id)
        return doc.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/content", mime_type="text/plain"
    )
    async def document_content_resource(document_id: int) -> str:
        return await client.documents.get_content(document_id)  # type: ignore[no-any-return]

    @mcp.resource(
        uri="paperless://documents/{document_id}/metadata",
        mime_type="application/json",
    )
    async def document_metadata_resource(document_id: int) -> str:
        meta = await client.documents.get_metadata(document_id)
        return meta.model_dump_json()

    @mcp.resource(
        uri="paperless://documents/{document_id}/notes", mime_type="application/json"
    )
    async def document_notes_resource(document_id: int) -> str:
        notes = await client.documents.get_notes(document_id)
        return "[" + ",".join(n.model_dump_json() for n in notes) + "]"

    @mcp.resource(
        uri="paperless://documents/{document_id}/history", mime_type="application/json"
    )
    async def document_history_resource(document_id: int) -> str:
        entries = await client.documents.get_history(document_id)
        return "[" + ",".join(e.model_dump_json() for e in entries) + "]"

    @mcp.resource(
        uri="paperless://documents/{document_id}/thumbnail", mime_type="image/png"
    )
    async def document_thumbnail_resource(document_id: int) -> bytes:
        data, _ = await client.documents.get_thumbnail(document_id)
        return data  # type: ignore[return-value]

    @mcp.resource(
        uri="paperless://documents/{document_id}/preview", mime_type="application/pdf"
    )
    async def document_preview_resource(document_id: int) -> bytes:
        data, _ = await client.documents.get_preview(document_id)
        return data  # type: ignore[return-value]

    @mcp.resource(
        uri="paperless://documents/{document_id}/download",
        mime_type="application/octet-stream",
    )
    async def document_download_resource(document_id: int) -> bytes:
        data, _ = await client.documents.download(document_id)
        return data  # type: ignore[return-value]
