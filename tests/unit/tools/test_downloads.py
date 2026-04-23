"""Tests for download tools."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from paperless_mcp.tools import downloads as downloads_mod
from paperless_mcp.tools._context import ToolContext


def _mock_client() -> Any:
    client = MagicMock()
    client.documents.download = AsyncMock(return_value=(b"PDF-bytes", "application/pdf"))
    client.documents.get_preview = AsyncMock(return_value=(b"preview-bytes", "image/png"))
    client.documents.get_thumbnail = AsyncMock(return_value=(b"thumb-bytes", "image/png"))
    client.documents.get = AsyncMock()
    return client


def _mock_artifact_store() -> Any:
    store = MagicMock()
    store.put_ephemeral = AsyncMock(return_value="https://artifacts.example/abc")
    return store


def _names(mcp: FastMCP) -> set[str]:
    tools = asyncio.run(mcp.list_tools())
    return {t.name for t in tools}


def test_registers_with_artifact_store() -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=_mock_client(),
        read_only=False,
        default_page_size=25,
        artifact_store=_mock_artifact_store(),
    )
    downloads_mod.register(mcp, ctx)
    assert "create_download_link" in _names(mcp)


def test_skips_registration_without_artifact_store() -> None:
    mcp = FastMCP("test")
    ctx = ToolContext(
        client=_mock_client(),
        read_only=False,
        default_page_size=25,
        artifact_store=None,
    )
    downloads_mod.register(mcp, ctx)
    assert "create_download_link" not in _names(mcp)
