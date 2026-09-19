"""Document capability links over the public pvl-core transfer API.

External contracts: ``docs/design/reference/core-transfer-links.md``.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Annotated, Any
from uuid import uuid4

from fastmcp_pvl_core import (
    TransferReadResult,
    TransferSinkError,
    add_transfer_workflow,
    build_kv_store,
    build_transfer_links,
)
from pydantic import Field

from paperless_mcp._transfer_models import (
    DocumentVariant,
    DownloadHandle,
    PositiveId,
    UploadHandle,
    UploadMetadata,
    render_markdown,
)
from paperless_mcp._transfer_uploads import UploadReceiver
from paperless_mcp.client._errors import PaperlessAPIError
from paperless_mcp.tools._registry import register_tool

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from paperless_mcp.config import ProjectConfig
    from paperless_mcp.tools._context import ToolContext


_DOWNLOAD_TOOL = "create_document_download_link"
_UPLOAD_TOOL = "create_document_upload_link"


class PaperlessTransferSink:
    """Read document representations and accept new files through Paperless."""

    def __init__(self, ctx: ToolContext, config: ProjectConfig) -> None:
        self._documents = ctx.client.documents
        self._config = config.server
        self._uploads = UploadReceiver(
            self._documents,
            build_kv_store(config.server, namespace="paperless-upload-receipts"),
            config.http_timeout_seconds,
        )

    def _check_visible(self, tool: str) -> None:
        # Old persisted links must also respect a newly restricted deployment.
        if tool in self._config.tools_deny or (
            self._config.tools_allow and tool not in self._config.tools_allow
        ):
            raise TransferSinkError(403)

    async def read(self, handle: str) -> TransferReadResult:
        """Read the requested representation using current Paperless permissions.

        Args:
            handle: A serialized, validated DownloadHandle.

        Returns:
            Bytes, media type and attachment filename for the HTTP response.
        """
        self._check_visible(_DOWNLOAD_TOOL)
        download = DownloadHandle.model_validate_json(handle)
        try:
            return await self._read_document(download)
        except PaperlessAPIError as exc:
            raise _transfer_error(exc) from exc

    async def _read_document(self, download: DownloadHandle) -> TransferReadResult:
        document = await self._documents.get(download.document_id)
        if download.variant == "content":
            return TransferReadResult(
                render_markdown(document), "text/markdown", f"document-{document.id}.md"
            )
        if download.variant == "preview":
            body, media_type = await self._documents.get_preview(document.id)
            filename = f"document-{document.id}-preview.pdf"
        else:
            original = download.variant == "original"
            if not original and not document.archived_file_name:
                raise TransferSinkError(404, "Document has no archived PDF")
            body, media_type = await self._documents.download(
                document.id, original=original
            )
            filename = (
                document.original_file_name if original else document.archived_file_name
            ) or f"document-{document.id}"
        return TransferReadResult(body, media_type, filename)

    async def write(self, handle: str, body: bytes) -> dict[str, Any]:
        """Submit raw file bytes and return the consume task ID without waiting.

        Args:
            handle: A serialized, validated UploadHandle.
            body: File bytes, including Markdown files, passed through unchanged.

        Returns:
            Paperless's task acknowledgement; identical retries reuse the receipt.
        """
        self._check_visible(_UPLOAD_TOOL)
        upload = UploadHandle.model_validate_json(handle)
        try:
            return await self._uploads.receive(upload, body)
        except PaperlessAPIError as exc:
            raise _transfer_error(exc) from exc


def _transfer_error(exc: PaperlessAPIError) -> TransferSinkError:
    status = exc.status_code if 400 <= exc.status_code < 500 else 502
    return TransferSinkError(status)


def register_transfers(mcp: FastMCP, ctx: ToolContext, config: ProjectConfig) -> None:
    """Mount transfer routes and register document-specific link tools.

    Args:
        mcp: HTTP server with a configured public base URL.
        ctx: The same Paperless context used by existing tools and resources.
        config: Server and transfer configuration.
    """
    links = build_transfer_links(
        mcp, config.server, config.transfer, sink=PaperlessTransferSink(ctx, config)
    )

    @register_tool(mcp, _DOWNLOAD_TOOL)
    async def create_document_download_link(
        document_id: PositiveId,
        variant: DocumentVariant = "original",
        ttl_s: Annotated[float | None, Field(gt=0, allow_inf_nan=False)] = None,
    ) -> dict[str, Any]:
        """Create an expiring link to a document file without returning its bytes.

        GET the URL externally to download it. Content returns the full OCR
        text as UTF-8 Markdown with title and metadata front matter; it does
        not infer formatting from OCR. Files are fetched at download time.
        An archive request fails if the document has no archived PDF.

        Args:
            document_id: Paperless document ID.
            variant: Original file, archived PDF, preview, or OCR content Markdown.
            ttl_s: Optional lifetime in seconds, capped at the configured maximum.

        Returns:
            URL and lifetime. The URL grants access without MCP credentials.
        """
        download = DownloadHandle(document_id=document_id, variant=variant)
        # Check existence and permissions before granting a capability.
        await ctx.client.documents.get(document_id)
        return await links.mint_download(download.model_dump_json(), ttl_s)

    @register_tool(mcp, _UPLOAD_TOOL, tags={"write"})
    async def create_document_upload_link(
        filename: str,
        metadata: UploadMetadata | None = None,
        ttl_s: Annotated[float | None, Field(gt=0, allow_inf_nan=False)] = None,
    ) -> dict[str, Any]:
        """Create an expiring link that accepts one new document, including Markdown.

        PUT raw file bytes to the URL (not JSON, base64, or multipart). The HTTP
        response returns task_id; use get_task to track consumption separately.
        Markdown bytes and filename are preserved. Paperless must recognize
        the file as a supported type; YAML front matter is not applied as
        document metadata. Supply metadata explicitly here.

        Identical retries return the same task ID. HTTP 409 means the bytes
        changed or an earlier upload's outcome is uncertain: inspect Paperless
        tasks before creating another link.

        Args:
            filename: Plain filename, such as invoice.pdf or notes.md.
            metadata: Optional title, tags and other Paperless upload fields.
            ttl_s: Optional lifetime in seconds, capped at the configured maximum.

        Returns:
            URL and lifetime. The URL grants upload access without MCP credentials.
        """
        upload = UploadHandle(
            operation_id=uuid4().hex,
            expires_at=time.time()
            + min(
                ttl_s if ttl_s is not None else config.transfer.ttl_default_s,
                config.transfer.ttl_max_s,
            ),
            filename=filename,
            metadata=metadata or UploadMetadata(),
        )
        return await links.mint_upload(upload.model_dump_json(), ttl_s)

    # Separate snippets retain the download workflow if uploads are hidden.
    add_transfer_workflow(mcp, download_tool=_DOWNLOAD_TOOL)
    add_transfer_workflow(mcp, upload_tool=_UPLOAD_TOOL)
