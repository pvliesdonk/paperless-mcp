"""Smoke test: the server boots with tools, resources, and prompts wired."""

from __future__ import annotations

import pytest
from fastmcp import FastMCP
from fastmcp_pvl_core import build_event_store, finalize_instructions, instructions_for

from paperless_mcp.config import ProjectConfig
from paperless_mcp.domain import add_instance_instructions
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


def test_instance_snippet_skipped_without_a_url() -> None:
    """A config carrying no Paperless URL contributes no snippet at all.

    ``make_server`` cannot reach this — registration fails first, without a URL
    there is no client — but ``ProjectConfig()`` with no arguments is legal, so
    the guard is the difference between silence and prose naming an empty host.
    """
    config = ProjectConfig()
    mcp: FastMCP = FastMCP(name="paperless-mcp")
    instructions_for(mcp).identity("paperless-mcp", "Paperless-NGX over MCP.")

    add_instance_instructions(mcp, config)
    finalize_instructions(mcp, config.server, env_prefix="PAPERLESS_MCP")

    assert mcp.instructions == "paperless-mcp: Paperless-NGX over MCP."


def test_sse_server_boots_without_artifact_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SSE construction does not depend on the retired download-store API."""
    monkeypatch.setenv("PAPERLESS_MCP_PAPERLESS_URL", "http://paperless.test")
    monkeypatch.setenv("PAPERLESS_MCP_API_TOKEN", "t")

    server = make_server(transport="sse")

    assert server is not None
