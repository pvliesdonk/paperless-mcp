"""Paperless-backed hooks for pvl-core's Transfer API (capability-link downloads).

``fastmcp_pvl_core.register_transfer_routes`` owns the token store, the
``/transfer/{token}`` route, and the generic ``create_download_link`` /
``create_upload_link`` tools (names, hints, icons). This module supplies the
one domain hook it consumes: a :class:`~fastmcp_pvl_core.TransferSink` plus its
``TransferValidator``.

A link ``ref`` (and the ``sink_handle`` it validates to) is a document ID,
optionally suffixed with a variant: ``"982"`` (original, the default),
``"982:archived"``, or ``"982:preview"``.

Uploads are not a Paperless concept this route can express — ``upload_document``
already covers document ingestion with real metadata (tags, correspondent,
document type). ``validate`` rejects ``kind="upload"`` so no upload token is
ever minted, and ``write`` is consequently unreachable.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastmcp_pvl_core import TransferReadResult

from paperless_mcp.client._errors import PaperlessAPIError

if TYPE_CHECKING:
    from collections.abc import Mapping

    from fastmcp_pvl_core import TransferKind

    from paperless_mcp.client import PaperlessClient

_VARIANTS = ("original", "archived", "preview")


def _parse_ref(ref: str) -> tuple[int, str]:
    """Split *ref* into ``(document_id, variant)``, defaulting variant to original.

    Raises:
        ValueError: The document id is not an integer, or the variant (if given)
            is not one of ``original``, ``archived``, ``preview``.
    """
    document_id_part, sep, variant = ref.partition(":")
    if not sep:
        variant = "original"
    if not document_id_part.isdigit():
        raise ValueError(f"ref must start with a numeric document id, got {ref!r}")
    if variant not in _VARIANTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {_VARIANTS}")
    return int(document_id_part), variant


class PaperlessTransferSink:
    """:class:`TransferSink` + validator backed by the Paperless REST API."""

    def __init__(self, client: PaperlessClient) -> None:
        self._client = client

    async def validate(self, ref: str, kind: TransferKind) -> str:
        """Validate a link ref; return the opaque sink handle or raise to reject.

        Args:
            ref: A document id, optionally suffixed ``:archived`` or ``:preview``.
            kind: Only ``"download"`` is supported.

        Returns:
            The normalized ``"<document_id>:<variant>"`` handle.

        Raises:
            ValueError: *kind* is ``"upload"``, *ref* is malformed, or the
                document does not exist.
        """
        if kind != "download":
            raise ValueError("paperless-mcp does not support upload links")
        document_id, variant = _parse_ref(ref)
        try:
            await self._client.documents.get(document_id)
        except PaperlessAPIError as exc:
            raise ValueError(f"document {document_id} not found") from exc
        return f"{document_id}:{variant}"

    async def read(self, handle: str) -> TransferReadResult:
        """Fetch the bytes for a download *handle*, at serve time (not mint time).

        Args:
            handle: A ``"<document_id>:<variant>"`` string, as returned by
                :meth:`validate`.

        Returns:
            The document (or preview) bytes, content type, and filename.
        """
        document_id, variant = _parse_ref(handle)
        document = await self._client.documents.get(document_id)
        raw_name = document.original_file_name or f"document-{document_id}"
        if variant == "preview":
            data, content_type = await self._client.documents.get_preview(document_id)
            p = Path(raw_name)
            filename = f"{p.stem}-preview{p.suffix}"
        else:
            data, content_type = await self._client.documents.download(
                document_id, original=(variant == "original")
            )
            filename = raw_name
        return TransferReadResult(data, content_type, filename)

    async def write(self, handle: str, body: bytes) -> Mapping[str, Any]:
        """Unreachable: :meth:`validate` never mints an upload token."""
        raise NotImplementedError(
            "paperless-mcp does not support uploads via create_upload_link"
        )
