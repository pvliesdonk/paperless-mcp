"""MCP prompts for paperless-mcp.

Deliberately minimal for v1 — no prompts ship.  Add as concrete user workflows
emerge (e.g. "find documents from correspondent X matching Y").
"""

# No ``from __future__ import annotations`` here: with postponed annotations
# FastMCP 4.0.5 cannot tell a ``str`` argument apart from a JSON one and
# appends "Provide a value matching the following JSON schema ..." to every
# prompt argument's description.
from fastmcp import FastMCP


def register_prompts(_mcp: FastMCP) -> None:
    """No prompts registered in v1."""
    return
