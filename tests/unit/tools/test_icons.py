"""Smoke tests for ICON_REGISTRY and ANNOTATION_REGISTRY."""

from __future__ import annotations

from paperless_mcp.tools._annotations import ANNOTATION_REGISTRY
from paperless_mcp.tools._icons import ICON_REGISTRY


def test_every_icon_entry_decodes() -> None:
    assert len(ICON_REGISTRY) > 0
    for tool_name, icons in ICON_REGISTRY.items():
        assert len(icons) >= 1, f"{tool_name} has no icons"
        for icon in icons:
            assert icon.src.startswith("data:image/svg+xml;base64,"), tool_name
            assert icon.mimeType == "image/svg+xml"


def test_registries_are_in_lockstep() -> None:
    icon_names = set(ICON_REGISTRY.keys())
    annotation_names = set(ANNOTATION_REGISTRY.keys())
    missing_annotations = icon_names - annotation_names
    missing_icons = annotation_names - icon_names
    assert not missing_annotations, f"no annotations for: {missing_annotations}"
    assert not missing_icons, f"no icons for: {missing_icons}"


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
