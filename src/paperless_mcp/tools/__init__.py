"""Tool registrations for Paperless MCP.

Each submodule exposes a ``register(mcp, ctx)`` function;
:func:`register_tools` wires everything together.
"""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp._domain_config import load_domain_config
from paperless_mcp.client import PaperlessClient
from paperless_mcp.tools import (
    correspondents,
    custom_fields,
    document_types,
    documents,
    downloads,
    saved_views,
    share_links,
    storage_paths,
    system,
    tags,
    tasks,
)
from paperless_mcp.tools._context import ToolContext


def _register_all(mcp: FastMCP, ctx: ToolContext) -> None:
    documents.register(mcp, ctx)
    tags.register(mcp, ctx)
    correspondents.register(mcp, ctx)
    document_types.register(mcp, ctx)
    custom_fields.register(mcp, ctx)
    storage_paths.register(mcp, ctx)
    saved_views.register(mcp, ctx)
    share_links.register(mcp, ctx)
    tasks.register(mcp, ctx)
    system.register(mcp, ctx)
    downloads.register(mcp, ctx)


def register_tools(mcp: FastMCP, *, read_only: bool = False) -> None:
    """Register every paperless-mcp tool on *mcp*.

    Args:
        mcp: The FastMCP server instance to register tools on.
        read_only: When ``True``, only read-only tools are registered.
    """
    cfg = load_domain_config()
    client = PaperlessClient(
        base_url=cfg.paperless_url,
        api_token=cfg.api_token.get_secret_value(),
        timeout_seconds=cfg.http_timeout_seconds,
        max_retries=cfg.http_retries,
    )
    ctx = ToolContext(
        client=client,
        read_only=read_only,
        default_page_size=cfg.default_page_size,
    )
    _register_all(mcp, ctx)
