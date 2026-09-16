"""Context shared across tool-registration modules."""

from __future__ import annotations

from dataclasses import dataclass

from paperless_mcp.client import PaperlessClient


@dataclass(frozen=True)
class ToolContext:
    """Per-server state passed to each tool-registration module.

    Attributes:
        client: Authenticated Paperless REST client.
        default_page_size: Default pagination window for list tools.
        public_url: Public Paperless UI base URL.  Used to construct
            user-visible links (set from ``ProjectConfig.public_url``).
    """

    client: PaperlessClient
    default_page_size: int
    public_url: str
