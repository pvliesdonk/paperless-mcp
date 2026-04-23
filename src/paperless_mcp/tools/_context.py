"""Context shared across tool-registration modules."""

from __future__ import annotations

from dataclasses import dataclass

from paperless_mcp.client import PaperlessClient


@dataclass(frozen=True)
class ToolContext:
    """Per-server state passed to each tool-registration module.

    Attributes:
        client: Authenticated Paperless REST client.
        read_only: Whether writable tools should be skipped.
        default_page_size: Default pagination window for list tools.
        artifact_store: Optional artifact store for download links; ``None``
            under stdio transport.
    """

    client: PaperlessClient
    read_only: bool
    default_page_size: int
    artifact_store: object | None = None
