"""MCP prompts for paperless-mcp.

Deliberately minimal for v1 — no prompts ship.  Add as concrete user workflows
emerge (e.g. "find documents from correspondent X matching Y").
"""

from __future__ import annotations

from fastmcp import FastMCP


def register_prompts(_mcp: FastMCP) -> None:
    """No prompts registered in v1."""
    return
