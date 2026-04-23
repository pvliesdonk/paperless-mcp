"""Helpers for registering MCP tools with icons, annotations, and read-only gating.

These are local utilities pending fastmcp-pvl-core#16 for upstream versions.

The helper looks up icons and annotations from per-tool registries by tool
name, so call sites stay compact: ``@register_tool(mcp, "list_tags",
read_only_mode=read_only)``.
"""

from __future__ import annotations

import base64
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from fastmcp import FastMCP
from mcp.types import Icon

F = TypeVar("F", bound=Callable[..., object])


def load_svg_data_uri(path: Path) -> str:
    """Read an SVG file and return it as an ``image/svg+xml`` data URI."""
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_icon(path: Path) -> Icon:
    """Build an :class:`Icon` pointing at the given SVG file."""
    return Icon(src=load_svg_data_uri(path), mimeType="image/svg+xml")


def register_tool(
    mcp: FastMCP,
    name: str,
    *,
    read_only_mode: bool = False,
    **tool_kwargs: object,
) -> Callable[[F], F]:
    """Return a decorator that registers *func* as an MCP tool named *name*.

    Looks up icons from :data:`paperless_mcp.tools._icons.ICON_REGISTRY`
    and annotations from :data:`paperless_mcp.tools._annotations.ANNOTATION_REGISTRY`.

    When ``read_only_mode`` is ``True`` and the tool's ``readOnlyHint`` is
    ``False``, the decorator returns the function unchanged (no registration).

    Raises:
        KeyError: If *name* is not present in either registry.
    """
    from paperless_mcp.tools._annotations import ANNOTATION_REGISTRY
    from paperless_mcp.tools._icons import ICON_REGISTRY

    icons = ICON_REGISTRY[name]
    annotations = ANNOTATION_REGISTRY[name]
    read_only_tool = bool(annotations.get("readOnlyHint", False))

    def decorator(func: F) -> F:
        if read_only_mode and not read_only_tool:
            return func
        return mcp.tool(
            name=name,
            icons=icons,
            annotations=dict(annotations),
            **tool_kwargs,  # type: ignore[arg-type]
        )(func)

    return decorator
