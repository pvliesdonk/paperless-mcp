"""Resource-module registry for Paperless MCP.

Each submodule exposes a ``register(mcp, ctx)`` function;
:func:`register_resources` wires everything together.
"""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp._domain_config import load_domain_config
from paperless_mcp.client import PaperlessClient
from paperless_mcp.resources import collections as _collections
from paperless_mcp.resources import documents as _documents
from paperless_mcp.resources import tasks as _tasks
from paperless_mcp.tools._context import ToolContext


def _register_all(mcp: FastMCP, ctx: ToolContext) -> None:
    _collections.register(mcp, ctx)
    _documents.register(mcp, ctx)
    _tasks.register(mcp, ctx)


def register_resources(
    mcp: FastMCP, ctx: ToolContext | None = None, *, read_only: bool = False
) -> None:
    """Register every paperless-mcp resource on *mcp*.

    Args:
        mcp: The FastMCP server instance to register resources on.
        ctx: Optional pre-built :class:`~paperless_mcp.tools._context.ToolContext`.
            When ``None``, a new client and context are created from env config.
        read_only: When ``True``, only read-only resources are registered.
            Ignored when *ctx* is supplied.
    """
    if ctx is None:
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
