"""Resource-module registry for Paperless MCP.

Each submodule exposes a ``register(mcp, ctx)`` function;
:func:`register_resources` wires everything together.
"""

from __future__ import annotations

from fastmcp import FastMCP

from paperless_mcp import domain
from paperless_mcp.resources import collections as _collections
from paperless_mcp.resources import documents as _documents
from paperless_mcp.resources import tasks as _tasks
from paperless_mcp.tools._context import ToolContext


def _register_all(mcp: FastMCP, ctx: ToolContext) -> None:
    _collections.register(mcp, ctx)
    _documents.register(mcp, ctx)
    _tasks.register(mcp, ctx)


def register_resources(mcp: FastMCP, ctx: ToolContext | None = None) -> None:
    """Register every paperless-mcp resource on *mcp*.

    Args:
        mcp: The FastMCP server instance to register resources on.
        ctx: Optional pre-built :class:`~paperless_mcp.tools._context.ToolContext`.
            When ``None``, the context staged by :func:`register_tools` is
            reused, or a new one is built from env config.
    """
    if ctx is None:
        ctx = domain.pending_tool_context() or domain.build_tool_context()
    _register_all(mcp, ctx)
