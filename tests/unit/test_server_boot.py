"""Smoke test: the server boots with tools, resources, and prompts wired."""

from __future__ import annotations

import pytest
from fastmcp_pvl_core import build_event_store

from paperless_mcp.config import ProjectConfig
from paperless_mcp.domain import pending_tool_context
from paperless_mcp.server import make_server


def test_server_boots_without_paperless(monkeypatch: pytest.MonkeyPatch) -> None:
    """make_server() registers tools and resources without hitting Paperless."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    server = make_server()
    assert server is not None


def test_http_server_boots_with_kv_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP app construction uses the configured KV-backed event store."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    monkeypatch.setenv("PAPERLESS_MCP_KV_STORE_URL", "memory://")
    config = ProjectConfig.from_env()
    server = make_server(transport="http", config=config)

    app = server.http_app(
        path="/mcp", event_store=build_event_store("PAPERLESS_MCP", config.server)
    )

    assert app is not None


def test_instructions_name_the_public_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    """The composed instructions state the instance URL and the URI patterns.

    The public URL is what tool results build ``web_url`` from, so it is the one
    a link in conversation will match; the internal API URL the server calls is
    not, and must not reach the model as this instance's identity.
    """
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.internal:8000")
    monkeypatch.setenv(
        "PAPERLESS_MCP_PAPERLESS_PUBLIC_URL", "https://paperless.example.org"
    )
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")

    text = make_server().instructions or ""

    assert "Paperless-NGX instance at https://paperless.example.org." in text
    assert "https://paperless.example.org/documents/<id>/" in text
    assert "paperless://documents/<id>" in text
    assert "tags://paperless" in text
    assert "paperless.internal" not in text


def test_instructions_fall_back_to_the_api_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a public URL, the API URL is the instance the snippet names.

    ``public_url`` resolves the fallback, so this pins that the snippet reads it
    through that property rather than the raw optional field.
    """
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "https://paperless.example.org")
    monkeypatch.delenv("PAPERLESS_MCP_PAPERLESS_PUBLIC_URL", raising=False)
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")

    text = make_server().instructions or ""

    assert "Paperless-NGX instance at https://paperless.example.org." in text


def test_instance_snippet_names_the_url_tool_results_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The snippet follows the staged context, not ``make_server``'s config.

    ``register_tools`` builds its context from the environment, so a config
    passed to ``make_server`` does not reach the Paperless client
    (pvliesdonk/fastmcp-server-template#622). Reading that config for the
    snippet would let the instructions name one instance while every ``web_url``
    in a tool result named another, so this pins which of the two wins.
    """
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "https://env.example.org")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")
    # No token: this config is never used to build a Paperless client, which is
    # precisely what the test is about.
    passed = ProjectConfig(paperless_url="https://passed.example.org")

    text = make_server(config=passed).instructions or ""

    staged = pending_tool_context()
    assert staged is not None
    assert staged.public_url == "https://env.example.org"
    assert "Paperless-NGX instance at https://env.example.org." in text
    assert "passed.example.org" not in text


def test_sse_server_boots_without_artifact_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SSE construction does not depend on the retired download-store API."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")

    server = make_server(transport="sse")

    assert server is not None
