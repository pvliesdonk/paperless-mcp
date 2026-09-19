"""Upload receipts prevent the core transfer grace window from re-enqueuing files.

See ``docs/design/reference/core-transfer-links.md`` for replay semantics.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import TYPE_CHECKING, Any

from fastmcp_pvl_core import TransferSinkError

if TYPE_CHECKING:
    from key_value.aio.protocols.key_value import AsyncKeyValue

    from paperless_mcp._transfer_models import UploadHandle
    from paperless_mcp.client.documents import DocumentsClient


class UploadReceiver:
    """Submit each upload operation once and retain its Paperless task receipt.

    A pending receipt is persisted before the POST. If the POST outcome is
    unknown, retries return 409 instead of risking a second consume job.
    The lock follows core's single-process concurrency contract.
    """

    def __init__(
        self, documents: DocumentsClient, store: AsyncKeyValue, timeout: float
    ) -> None:
        self._documents = documents
        self._store = store
        self._timeout = timeout
        self._lock = asyncio.Lock()

    async def receive(self, upload: UploadHandle, body: bytes) -> dict[str, Any]:
        """Return the upload task acknowledgement, including on identical retries.

        Args:
            upload: Validated destination and unique operation ID.
            body: Raw file bytes, bounded by the transfer route's upload cap.

        Returns:
            The Paperless task acknowledgement as JSON-compatible data.

        Raises:
            TransferSinkError: A retry changed bytes or has an uncertain outcome.
        """
        digest = hashlib.sha256(body).hexdigest()
        ttl = max(upload.expires_at - time.time(), 0) + self._timeout
        async with self._lock:
            previous = await self._store.get(upload.operation_id)
            if previous is not None:
                return self._replay(previous, digest)
            await self._store.put(upload.operation_id, {"digest": digest}, ttl=ttl)
        # No lock across network I/O: unrelated files may upload concurrently.
        result = await self._documents.upload(
            filename=upload.filename,
            content=body,
            **upload.metadata.model_dump(exclude_none=True),
        )
        payload = result.model_dump(mode="json")
        await self._store.put(
            upload.operation_id, {"digest": digest, "result": payload}, ttl=ttl
        )
        return payload

    @staticmethod
    def _replay(previous: dict[str, Any], digest: str) -> dict[str, Any]:
        if previous["digest"] != digest:
            raise TransferSinkError(
                409, "Upload link already used with different bytes"
            )
        if "result" not in previous:
            raise TransferSinkError(
                409, "Upload outcome pending; inspect Paperless tasks"
            )
        return dict(previous["result"])
