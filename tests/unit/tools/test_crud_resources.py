"""Registration tests for CRUD resource tool modules."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from paperless_mcp.tools import (
    correspondents as correspondents_mod,
)
from paperless_mcp.tools import (
    custom_fields as custom_fields_mod,
)
from paperless_mcp.tools import (
    document_types as document_types_mod,
)
from paperless_mcp.tools import (
    tags as tags_mod,
)
from paperless_mcp.tools._context import ToolContext


def _mock_client() -> Any:
    client = MagicMock()
    for attr in ("tags", "correspondents", "document_types", "custom_fields"):
        sub = getattr(client, attr)
        for meth in ("list", "get", "create", "update", "delete", "bulk_edit"):
            setattr(sub, meth, AsyncMock())
    return client


def _names(mcp: FastMCP) -> set[str]:
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


@pytest.mark.parametrize(
    ("module", "prefix"),
    [
        (tags_mod, "tag"),
        (correspondents_mod, "correspondent"),
        (document_types_mod, "document_type"),
        (custom_fields_mod, "custom_field"),
    ],
)
def test_read_only_registers_read_tools_only(module: Any, prefix: str) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), read_only=True, default_page_size=25)
    module.register(mcp, ctx)
    names = _names(mcp)
    assert f"list_{prefix}s" in names
    assert f"get_{prefix}" in names
    assert f"create_{prefix}" not in names
    assert f"update_{prefix}" not in names
    assert f"delete_{prefix}" not in names
    assert f"bulk_edit_{prefix}s" not in names


@pytest.mark.parametrize(
    ("module", "prefix"),
    [
        (tags_mod, "tag"),
        (correspondents_mod, "correspondent"),
        (document_types_mod, "document_type"),
        (custom_fields_mod, "custom_field"),
    ],
)
def test_all_tools_have_icons(module: Any, prefix: str) -> None:
    from paperless_mcp.tools._icons import ICON_REGISTRY

    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), read_only=False, default_page_size=25)
    module.register(mcp, ctx)
    names = _names(mcp)
    for name in names:
        assert name in ICON_REGISTRY, f"tool {name!r} missing from ICON_REGISTRY"


@pytest.mark.parametrize(
    ("module", "prefix"),
    [
        (tags_mod, "tag"),
        (correspondents_mod, "correspondent"),
        (document_types_mod, "document_type"),
        (custom_fields_mod, "custom_field"),
    ],
)
def test_read_write_registers_all(module: Any, prefix: str) -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), read_only=False, default_page_size=25)
    module.register(mcp, ctx)
    names = _names(mcp)
    expected = {
        f"list_{prefix}s",
        f"get_{prefix}",
        f"create_{prefix}",
        f"update_{prefix}",
        f"delete_{prefix}",
        f"bulk_edit_{prefix}s",
    }
    assert expected.issubset(names)


def test_custom_field_tool_descriptions_mention_select_options() -> None:
    """Regression test: docstrings document extra_data.select_options shape."""
    mcp = FastMCP("test")
    ctx = ToolContext(client=_mock_client(), read_only=False, default_page_size=25)
    custom_fields_mod.register(mcp, ctx)
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    for name in ("create_custom_field", "update_custom_field"):
        desc = tools[name].description or ""
        assert "select_options" in desc, (
            f"Tool {name!r} description must mention 'select_options'; got: {desc!r}"
        )
