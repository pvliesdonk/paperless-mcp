"""Tool registrations for Paperless MCP.

Each submodule exposes a ``register(mcp, ctx)`` function;
:func:`register_tools` wires everything together.
"""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp import domain
from paperless_mcp.tools import (
    correspondents,
    custom_fields,
    document_types,
    documents,
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


def register_tools(mcp: FastMCP, ctx: ToolContext | None = None) -> None:
    """Register every paperless-mcp tool on *mcp*.

    Args:
        mcp: The FastMCP server instance to register tools on.
        ctx: Optional pre-built :class:`~paperless_mcp.tools._context.ToolContext`.
            When ``None``, the context :mod:`paperless_mcp.domain` shares
            with :func:`~paperless_mcp.resources.register_resources` is used,
            built from env config on whichever of the two runs first.
    """
    if ctx is None:
        ctx = domain.tool_context_for(mcp)
    _register_all(mcp, ctx)
