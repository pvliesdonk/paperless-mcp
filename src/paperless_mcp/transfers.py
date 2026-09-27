"""Document capability links over the public pvl-core transfer API.

External contracts: ``docs/design/reference/core-transfer-links.md``.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from fastmcp.exceptions import ToolError
from fastmcp_pvl_core import (
    TransferReadResult,
    TransferSinkError,
    build_kv_store,
    register_transfer_routes,
)
from pydantic import ValidationError as PydanticValidationError

from paperless_mcp._transfer_models import (
    DownloadHandle,
    UploadHandle,
    UploadReference,
    render_markdown,
)
from paperless_mcp._transfer_uploads import UploadReceiver
from paperless_mcp.client._errors import PaperlessAPIError
from paperless_mcp.tools._errors import raise_classified

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from paperless_mcp.config import ProjectConfig
    from paperless_mcp.tools._context import ToolContext


_RefT = TypeVar("_RefT", DownloadHandle, UploadReference)

_DOWNLOAD_TOOL = "create_download_link"
_UPLOAD_TOOL = "create_upload_link"


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


def _parse_ref(model: type[_RefT], ref: str, tool: str) -> _RefT:
    """Parse the model's ref; a bad one is the model's to fix (INFO).

    Only the ref is parsed here, so a pydantic error from Paperless's own reply,
    raised later, is not mistaken for a mistake in the ref: it reaches the tool
    boundary as a server fault instead.
    """
    try:
        return model.model_validate_json(ref)
    except PydanticValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first.get("loc", ())) or "ref"
        raise ToolError(
            f"The ref passed to {tool} is not valid at {where}: {first.get('msg')}. "
            f"Correct the ref and call {tool} again.",
            log_level=logging.INFO,
        ) from exc


async def _validate_download(ctx: ToolContext, ref: str) -> str:
    download = _parse_ref(DownloadHandle, ref, _DOWNLOAD_TOOL)
    try:
        document = await ctx.client.documents.get(download.document_id)
    except PaperlessAPIError as exc:
        raise_classified(exc, _DOWNLOAD_TOOL, {"ref.document_id": download.document_id})
    if download.variant == "archive" and not document.archived_file_name:
        raise ToolError(
            f"Document {document.id} has no archived PDF, so there is nothing to "
            "download for variant archive. Call create_download_link again with "
            'variant "original".',
            log_level=logging.INFO,
        )
    return download.model_dump_json()


def _validate_upload(ref: str, ttl_max_s: float) -> str:
    destination = _parse_ref(UploadReference, ref, _UPLOAD_TOOL)
    # Core's validator does not receive ttl_s. Retain receipts for the
    # maximum possible link lifetime; core alone resolves the actual TTL.
    upload = UploadHandle(
        **destination.model_dump(),
        operation_id=uuid4().hex,
        expires_at=time.time() + ttl_max_s,
    )
    return upload.model_dump_json()


def register_transfers(mcp: FastMCP, ctx: ToolContext, config: ProjectConfig) -> None:
    """Register core transfer tools with Paperless reference validation.

    Args:
        mcp: HTTP server with a configured public base URL.
        ctx: The same Paperless context used by existing tools and resources.
        config: Server and transfer configuration.
    """

    async def validate(ref: str, kind: str) -> str:
        """Resolve a JSON reference into a server-owned Paperless handle.

        Args:
            ref: Document selection or upload destination encoded as JSON.
            kind: Transfer direction supplied by core: download or upload.

        Returns:
            Validated serialized handle for the transfer sink.
        """
        if kind == "download":
            return await _validate_download(ctx, ref)
        return _validate_upload(ref, config.transfer.ttl_max_s)

    register_transfer_routes(
        mcp,
        config.server,
        config.transfer,
        sink=PaperlessTransferSink(ctx, config),
        validate=validate,
        download_note=(
            "ref is a JSON string naming a document and the file to serve, e.g. "
            '{"document_id":42,"variant":"content"}. variant is original (the '
            "file as uploaded, the default), archive (the searchable PDF), "
            "preview (the rendition Paperless displays) or content (the full "
            "text as Markdown, with the metadata as front matter)."
        ),
        upload_note=(
            "ref is a JSON string with a plain file name and optional metadata, e.g. "
            '{"filename":"scan.pdf","metadata":{"title":"Scan","tags":[2]}}; '
            "metadata takes title, correspondent, document_type, tags, created, "
            "archive_serial_number and custom_fields. PUT the file's raw bytes to "
            "the url; the answer carries the consume task_id for wait_for_task, "
            "and resending the same bytes returns the same task_id. Front matter "
            "in a Markdown file stays part of the file, not the metadata."
        ),
    )
