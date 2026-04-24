"""Tests for the DomainConfig loader."""

from __future__ import annotations

import pytest

from paperless_mcp._domain_config import load_domain_config


def test_required_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless:8000")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "abc")
    cfg = load_domain_config()
    assert cfg.paperless_url == "http://paperless:8000"
    assert cfg.api_token.get_secret_value() == "abc"
    assert cfg.http_timeout_seconds == 30
    assert cfg.http_retries == 2
    assert cfg.download_link_ttl_seconds == 300
    assert cfg.default_page_size == 25


def test_missing_required_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PAPERLESS_MCP_PAPERLESS_URL", raising=False)
    monkeypatch.delenv("PAPERLESS_MCP_API_TOKEN", raising=False)
    with pytest.raises(ValueError, match="PAPERLESS_MCP_PAPERLESS_URL"):
        load_domain_config()


def test_page_size_clamped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless:8000")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "abc")
    monkeypatch.setenv("PAPERLESS_MCP_DEFAULT_PAGE_SIZE", "500")
    with pytest.raises(ValueError, match="default_page_size"):
        load_domain_config()


def test_ttl_clamped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless:8000")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "abc")
    monkeypatch.setenv("PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS", "10")
    with pytest.raises(ValueError, match="download_link_ttl_seconds"):
        load_domain_config()


def test_trailing_slash_stripped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless:8000/")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "abc")
    cfg = load_domain_config()
    assert cfg.paperless_url == "http://paperless:8000"


def test_public_url_defaults_to_paperless_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.internal:8000")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    from paperless_mcp._domain_config import load_domain_config

    cfg = load_domain_config()
    assert cfg.paperless_url == "http://paperless.internal:8000"
    assert cfg.paperless_public_url == "http://paperless.internal:8000"


def test_public_url_can_be_overridden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.internal:8000")
    monkeypatch.setenv(
        "PAPERLESS_MCP_PAPERLESS_PUBLIC_URL", "https://docs.example.com/"
    )
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    from paperless_mcp._domain_config import load_domain_config

    cfg = load_domain_config()
    assert cfg.paperless_url == "http://paperless.internal:8000"
    # Trailing slash stripped to match paperless_url behaviour
    assert cfg.paperless_public_url == "https://docs.example.com"
