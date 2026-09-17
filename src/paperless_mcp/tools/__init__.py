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

# SPIKE (#110): the domain sentence appended to pvl-core's generic
# `get_job_result` description.  The numbers come from the task history of the
# deployed instance — see docs/design/long-running-calls.md.
_JOBS_NOTE = (
    "Paperless queues document consumption: an uploaded document typically "
    "waits about 45 seconds before the worker starts it, and occasionally "
    "several minutes, while the OCR itself takes only a second or two. "
    "`wait_for_task` therefore commonly answers with a job_id rather than a "
    "task; a consume that finishes quickly answers inline, with no job."
)


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
    # SPIKE (#110): the single server-wide poller.  Registered once, after the
    # category modules, so every handle — whichever tool minted it — resolves
    # through one contract.
    if ctx.jobs is not None:
        from fastmcp_pvl_core import register_job_tools

        register_job_tools(mcp, ctx.jobs, note=_JOBS_NOTE)
