"""Domain metadata passed directly to FastMCP or core registrars.

Registration contracts: docs/design/reference/core-tool-registration.md.
"""

from __future__ import annotations

from typing import TypedDict

from mcp.types import Icon, ToolAnnotations

from paperless_mcp.tools._annotations import ANNOTATION_REGISTRY
from paperless_mcp.tools._icons import ICON_REGISTRY
from paperless_mcp.tools._titles import TITLE_REGISTRY


class ToolMetadata(TypedDict):
    """Tool identity accepted by FastMCP and core's Jobs Path 1 registrar."""

    name: str
    icons: list[Icon]
    annotations: ToolAnnotations


def tool_metadata(name: str) -> ToolMetadata:
    """Return domain metadata without wrapping or registering a callable.

    Args:
        name: Tool name present in the domain metadata registries.

    Returns:
        Fresh registration kwargs, including the title and behavioral hints.

    Raises:
        KeyError: The tool is missing from a metadata registry.
    """
    return ToolMetadata(
        name=name,
        icons=list(ICON_REGISTRY[name]),
        annotations=ToolAnnotations(
            title=TITLE_REGISTRY[name], **ANNOTATION_REGISTRY[name]
        ),
    )
