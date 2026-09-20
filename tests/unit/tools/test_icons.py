"""Smoke tests for ICON_REGISTRY, ANNOTATION_REGISTRY and TITLE_REGISTRY."""

from __future__ import annotations

import asyncio

from fastmcp_pvl_core import ServerConfig

from paperless_mcp.config import ProjectConfig
from paperless_mcp.server import make_server
from paperless_mcp.tools._annotations import ANNOTATION_REGISTRY
from paperless_mcp.tools._icons import ICON_REGISTRY
from paperless_mcp.tools._titles import TITLE_REGISTRY


def test_every_icon_entry_decodes() -> None:
    assert len(ICON_REGISTRY) > 0
    for tool_name, icons in ICON_REGISTRY.items():
        assert len(icons) >= 1, f"{tool_name} has no icons"
        for icon in icons:
            assert icon.src.startswith("data:image/svg+xml;base64,"), tool_name
            assert icon.mime_type == "image/svg+xml"


def test_registries_are_in_lockstep() -> None:
    icon_names = set(ICON_REGISTRY.keys())
    annotation_names = set(ANNOTATION_REGISTRY.keys())
    title_names = set(TITLE_REGISTRY.keys())
    assert not icon_names - annotation_names, (
        f"no annotations for: {icon_names - annotation_names}"
    )
    assert not annotation_names - icon_names, (
        f"no icons for: {annotation_names - icon_names}"
    )
    assert not icon_names - title_names, f"no titles for: {icon_names - title_names}"
    assert not title_names - icon_names, (
        f"titles for unregistered tools: {title_names - icon_names}"
    )


def test_every_title_is_a_non_empty_string() -> None:
    for tool_name, title in TITLE_REGISTRY.items():
        assert isinstance(title, str), f"{tool_name} title is not a string"
        assert title.strip(), f"{tool_name} has a blank title"


def test_every_registered_tool_carries_a_title() -> None:
    """Every tool the server registers carries a non-empty ``annotations.title``.

    This is the enforcement sweep the Tool Registration Checklist asks for: a
    tool added without a title fails here rather than silently shipping its
    machine name as its label in title-aware clients.

    It enumerates the *full* registry rather than a client's ``tools/list`` so
    that a tool hidden by operator visibility cannot slip past untitled, and it
    therefore also covers ``get_server_info``, which ``fastmcp-pvl-core``
    registers rather than this repo's ``register_tool``.  ``_list_tools`` is
    private because FastMCP publishes no public accessor for the unfiltered
    set; the filtered listing would defeat the point of the sweep.
    """
    server = make_server(
        transport="http",
        config=ProjectConfig(
            server=ServerConfig(base_url="http://test", kv_store_url="memory://")
        ),
    )
    tools = asyncio.run(server._list_tools())

    untitled = [
        tool.name
        for tool in tools
        if not (tool.annotations and (tool.annotations.title or "").strip())
    ]
    assert not untitled, f"tools without annotations.title: {untitled}"
    # The sweep must reach past this repo's own registry, or it would prove
    # nothing the registry tests above do not already prove.
    assert set(TITLE_REGISTRY) < {tool.name for tool in tools}


def test_every_annotation_has_four_hints() -> None:
    required = {"readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}
    for tool_name, hints in ANNOTATION_REGISTRY.items():
        assert required.issubset(hints.keys()), tool_name
        for hint, value in hints.items():
            assert isinstance(value, bool), f"{tool_name}.{hint} is not bool"


def test_destructive_implies_not_read_only() -> None:
    for tool_name, hints in ANNOTATION_REGISTRY.items():
        if hints["destructiveHint"]:
            assert not hints["readOnlyHint"], (
                f"{tool_name}: destructive tool marked read-only"
            )
