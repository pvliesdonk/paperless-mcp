"""Tests for ProjectConfig composition."""

from __future__ import annotations

import pytest

from paperless_mcp.config import ProjectConfig


def test_from_env_composes_transfer_config_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PAPERLESS_MCP_TRANSFER_TTL_DEFAULT_S", raising=False)
    cfg = ProjectConfig.from_env()
    assert cfg.transfer.ttl_default_s == 3600.0


def test_from_env_reads_transfer_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_TRANSFER_TTL_DEFAULT_S", "120")
    cfg = ProjectConfig.from_env()
    assert cfg.transfer.ttl_default_s == 120.0
