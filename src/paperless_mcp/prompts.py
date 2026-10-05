"""MCP prompts for paperless-mcp.

Deliberately minimal for v1 — no prompts ship.  Add as concrete user workflows
emerge (e.g. "find documents from correspondent X matching Y").
"""

# No ``from __future__ import annotations`` here: with postponed annotations
# FastMCP 4.0.5 cannot tell a ``str`` argument apart from a JSON one and
# appends "Provide a value matching the following JSON schema ..." to every
# prompt argument's description.
from fastmcp import FastMCP


<<<<<<< before updating
def register_prompts(_mcp: FastMCP) -> None:
    """No prompts registered in v1."""
    return
=======
def register_prompts(mcp: FastMCP) -> None:
    """Register all domain prompts on *mcp*."""

    # The docstring summary is the prompt description a client shows in its
    # prompt picker; each ``Args:`` entry becomes that argument's
    # description (without one FastMCP emits a generic JSON-schema
    # sentence).  See https://gofastmcp.com/servers/prompts#prompt-arguments
    # for the full signature surface.
    @mcp.prompt()
    async def summarize(context: str) -> str:
        """Summarize a passage in one paragraph.

        Args:
            context: The passage.
        """
        return f"Summarize the following in one paragraph:\n\n{context}"
>>>>>>> after updating
