"""MCP tool registrations for downloads.

``create_download_link`` requires an artifact store on :class:`ToolContext`;
it is only registered when one is available (HTTP/SSE — stdio has no store).

ArtifactStore API investigation (J1): The upstream ``fastmcp_pvl_core``
``ArtifactStore`` exposes ``add(content, *, filename, mime_type) -> str``
which returns an opaque one-time token.  A ``put_ephemeral`` helper
(proposed interface: ``put_ephemeral(data, *, content_type, filename,
ttl_seconds, one_time) -> url_str``) does not yet exist in the upstream
library.  Upstream issue filed: pvliesdonk/fastmcp-pvl-core — "ArtifactStore:
confirm/add put_ephemeral(bytes, content_type, ttl) → URL".

Until then, callers of this module are expected to pass an artifact-store
adapter that provides ``put_ephemeral``; the ``type: ignore[attr-defined]``
suppresses mypy on the call site.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from paperless_mcp.models.common import DownloadLink
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.tools._registry import register_tool


def register(mcp: FastMCP, ctx: ToolContext) -> None:
    """Register download tools on *mcp* if an artifact store is present.

    If ``ctx.artifact_store`` is ``None`` (stdio transport), no tools are
    registered.

    Args:
        mcp: The FastMCP server instance.
        ctx: Tool context with client, read-only flag, and optional store.
    """
    if ctx.artifact_store is None:
        return

    client = ctx.client
    store = ctx.artifact_store
    read_only = ctx.read_only

    @register_tool(mcp, "create_download_link", read_only_mode=read_only)
    async def create_download_link(
        document_id: int,
        variant: Literal["original", "archived", "preview"] = "original",
        ttl_seconds: Annotated[int, Field(ge=30, le=3600)] = 300,
    ) -> DownloadLink:
        """Issue a one-time, unauthenticated HTTP URL serving the document.

        The URL is valid for ``ttl_seconds`` seconds **or** a single fetch,
        whichever comes first.  Works only when the MCP server runs over
        HTTP/SSE — stdio transports lack an artifact store.
        """
        if variant == "preview":
            data, content_type = await client.documents.get_preview(document_id)
            suffix = ".preview"
        else:
            data, content_type = await client.documents.download(
                document_id, original=(variant == "original")
            )
            suffix = ""

        document = await client.documents.get(document_id)
        base_name = document.original_file_name or f"document-{document_id}"
        if suffix and not base_name.endswith(suffix):
            base_name = f"{base_name}{suffix}"

        url = await store.put_ephemeral(  # type: ignore[attr-defined]
            data,
            content_type=content_type,
            filename=base_name,
            ttl_seconds=ttl_seconds,
            one_time=True,
        )
        return DownloadLink(
            download_url=url,
            expires_in_seconds=ttl_seconds,
            content_type=content_type,
            filename=base_name,
        )
