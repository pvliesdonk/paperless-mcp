"""Smoke tests for Paperless MCP."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx
from fastmcp import Client

from paperless_mcp._server_apps import register_apps
from paperless_mcp.config import ProjectConfig
from paperless_mcp.domain import tool_context_for
from paperless_mcp.server import make_server


def test_make_server_constructs() -> None:
    """make_server() returns a FastMCP instance without raising."""
    server = make_server()
    assert server is not None


def test_register_apps_logs_when_app_domain_set(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """register_apps logs the configured app domain when the env var is set.

    Covers the ``if app_domain:`` branch of ``_server_apps.register_apps``,
    which the default smoke tests miss because no ``PAPERLESS_MCP_APP_DOMAIN``
    is set in the test env.  Pass a real ``FastMCP`` instance so the test
    keeps working if a downstream maintainer adds real registrations to the
    branch (the scaffold's no-op branch ignores the argument today).
    """
    monkeypatch.setenv("PAPERLESS_MCP_APP_DOMAIN", "example.com")
    with caplog.at_level("INFO", logger="paperless_mcp._server_apps"):
        register_apps(make_server())
    # Assert on the structured log argument by exact equality rather than a
    # substring test of the formatted message.  ``"example.com" in r.message``
    # trips CodeQL's ``py/incomplete-url-substring-sanitization`` rule on the
    # host-shaped literal, even though this is a log assertion and not URL
    # sanitization; ``==`` is not a substring-membership pattern, so it does
    # not.  The branch logs the configured domain as its sole ``%s`` arg.
    assert any(r.args == ("example.com",) for r in caplog.records)


def _payload(result: Any) -> dict[str, Any]:
    """Decode a tool result's single text block."""
    first = result.content[0]
    assert hasattr(first, "text"), (
        f"expected text tool content, got {type(first).__name__}"
    )
    decoded: dict[str, Any] = json.loads(first.text)
    return decoded


async def test_get_server_info_tool_registered(
    client: Client[Any], paperless_base_url: str
) -> None:
    """``get_server_info`` reports the wrapper info and the *installed* Paperless.

    This project wires an upstream provider inside the ``DOMAIN-UPSTREAM``
    sentinel in ``server.py``, so the block is keyed ``paperless`` rather
    than absent — the scaffold's default ``upstream`` key is still unused.

    The mocked instance runs 2.14.7 while 2.20.14 is the newest release
    published upstream, so the two answers differ. That divergence is the
    point: ``/api/remote_version/`` reports the newest *release*, and reading
    it as the connected instance's version is the defect this test locks out.
    """
    tools = {t.name for t in await client.list_tools()}
    assert "get_server_info" in tools

    # assert_all_called=False: the remote-version route is registered precisely
    # so the test can assert nothing calls it.
    async with respx.mock(base_url=paperless_base_url, assert_all_called=False) as mock:
        mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json={"settings": {"version": "2.14.7"}})
        )
        remote = mock.get("/api/remote_version/").mock(
            return_value=httpx.Response(
                200, json={"version": "2.20.14", "update_available": True}
            )
        )
        result = await client.call_tool("get_server_info", {})
    payload = _payload(result)
    assert payload["server_name"] == "paperless-mcp"
    assert "server_version" in payload
    assert "core_version" in payload
    assert payload["paperless"] == {"version": "2.14.7"}
    assert not remote.called, (
        "get_server_info must not read /api/remote_version/ — that endpoint "
        "answers 'is an update available', which is get_remote_version's job"
    )
    # The default label stays unused: the block is keyed by upstream_label.
    assert "upstream" not in payload


async def test_get_server_info_reports_one_request(
    client: Client[Any], paperless_base_url: str
) -> None:
    """One HTTP request per call, to the endpoint that knows the installed version."""
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json={"settings": {"version": "2.14.7"}})
        )
        await client.call_tool("get_server_info", {})
    assert len(route.calls) == 1


async def test_get_server_info_survives_an_unreachable_paperless(
    client: Client[Any], paperless_base_url: str
) -> None:
    """An upstream failure must not fail the call that reports this build.

    The version is optional enrichment; the question the tool exists to answer
    ("is the latest fix deployed?") is about the wrapper, so the wrapper half
    has to come back even when Paperless does not.
    """
    async with respx.mock(base_url=paperless_base_url) as mock:
        mock.get("/api/ui_settings/").mock(side_effect=httpx.ConnectError("down"))
        result = await client.call_tool("get_server_info", {})
    payload = _payload(result)
    assert payload["server_version"]
    assert payload["paperless"] == {"version": None}


async def test_get_server_info_reuses_the_registered_paperless_client(
    server: Any, paperless_base_url: str
) -> None:
    """The provider must not open a second HTTP client.

    It captures the ToolContext ``register_tools`` staged, which is the one
    ``Service`` closes on shutdown; a provider that built its own client would
    leak it past the lifespan.
    """
    from paperless_mcp import domain

    staged = domain.pending_tool_context()
    assert staged is not None
    async with respx.mock(base_url=paperless_base_url) as mock:
        route = mock.get("/api/ui_settings/").mock(
            return_value=httpx.Response(200, json={"settings": {"version": "2.14.7"}})
        )
        async with Client(server) as connected:
            await connected.call_tool("get_server_info", {})
    assert route.called
    assert staged.client.http._client.is_closed, (
        "the lifespan closed the staged client, so the provider used that one"
    )


def test_server_name_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """``PAPERLESS_MCP_SERVER_NAME`` overrides the FastMCP server name.

    Unset, the name defaults to ``paperless-mcp`` (locked by the
    ``get_server_info`` test above). Set, ``make_server()`` must honor it so an
    operator can rename an instance without editing template-owned code.
    """
    monkeypatch.setenv("PAPERLESS_MCP_SERVER_NAME", "renamed-instance")
    server = make_server()
    assert server.name == "renamed-instance"
    assert (server.instructions or "").startswith(
        "renamed-instance: Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types."
    )


def test_server_name_env_override_reaches_server_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The overridden name also flows through to ``get_server_info``.

    ``register_server_info_tool`` is wired separately from the FastMCP ``name``,
    so this pins that both surfaces honor the same resolved name.
    """
    monkeypatch.setenv("PAPERLESS_MCP_SERVER_NAME", "renamed-instance")
    server = make_server()

    async def _call_server_info() -> Any:
        # Mocked: the upstream provider now runs on every call, and this test
        # is about the name, not the network.
        async with respx.mock(base_url="http://paperless.test") as mock:
            mock.get("/api/ui_settings/").mock(
                return_value=httpx.Response(
                    200, json={"settings": {"version": "2.14.7"}}
                )
            )
            async with Client(server) as smoke_client:
                return await smoke_client.call_tool("get_server_info", {})

    result = asyncio.run(_call_server_info())
    assert _payload(result)["server_name"] == "renamed-instance"


def test_instructions_env_override(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Legacy ``PAPERLESS_MCP_INSTRUCTIONS`` replaces all generated text and
    warns that both additive operator variables are ignored."""
    monkeypatch.setenv("PAPERLESS_MCP_INSTRUCTIONS", "Custom operator text.")
    monkeypatch.setenv("PAPERLESS_MCP_INSTANCE_DESCRIPTION", "Demo material.")
    monkeypatch.setenv("PAPERLESS_MCP_INSTRUCTIONS_EXTRA", "House rule: be brief.")
    # Scope to core's logger: make_server() re-applies FASTMCP_LOG_LEVEL to the
    # root logger, which would otherwise drop the record under a stricter env.
    monkeypatch.delenv("FASTMCP_LOG_LEVEL", raising=False)
    with caplog.at_level("WARNING", logger="fastmcp_pvl_core"):
        server = make_server()
    assert server.instructions == "Custom operator text."
    warning = next(
        rec.getMessage()
        for rec in caplog.records
        if "PAPERLESS_MCP_INSTRUCTIONS" in rec.getMessage()
    )
    assert "PAPERLESS_MCP_INSTANCE_DESCRIPTION" in warning
    assert "PAPERLESS_MCP_INSTRUCTIONS_EXTRA" in warning


def test_instructions_compose_semantic_operator_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Operator routing and policy retain their semantic positions."""
    monkeypatch.delenv("PAPERLESS_MCP_INSTRUCTIONS", raising=False)
    monkeypatch.setenv("PAPERLESS_MCP_INSTANCE_DESCRIPTION", "Demo material.")
    monkeypatch.setenv("PAPERLESS_MCP_INSTRUCTIONS_EXTRA", "House rule: be brief.")
    text = make_server().instructions or ""
    assert text.split("\n\n") == [
        "paperless-mcp: Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.",
        "Demo material.",
        "This server fronts the Paperless-NGX instance at http://paperless.test. "
        "A link of the form http://paperless.test/documents/<id>/ names a document "
        "by its id; pass that id to the document tools.",
        "House rule: be brief.",
        "Full documentation for this server: https://pvliesdonk.github.io/paperless-mcp/latest/llms.txt",
    ]


def test_instructions_name_the_instance_the_tools_call(
    paperless_api_token: str,
) -> None:
    """The instance named in the instructions is the one the tools call.

    The URL comes from the staged ``ToolContext``, so the instructions cannot
    name one Paperless while every ``web_url`` in a tool result points at
    another.  Asserting the two *agree* — rather than asserting which source
    wins — keeps this honest once a config passed to ``make_server`` reaches
    ``register_tools`` (pvliesdonk/fastmcp-server-template#622); today the
    environment wins on both sides, and afterwards the passed config will.
    """
    server = make_server(
        config=ProjectConfig(
            paperless_url="https://passed-in.example", api_token=paperless_api_token
        )
    )
    assert tool_context_for(server).public_url in (server.instructions or "")


def test_blank_overrides_fall_back_to_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Whitespace-only overrides fall back, honoring the "unset/empty" contract.

    ``env`` strips and treats a blank value as unset, so a blank SERVER_NAME
    must revert to ``paperless-mcp`` rather than rename the instance to
    whitespace, and a blank INSTRUCTIONS must leave the composed text in place.
    Guards against a future refactor (e.g. raw ``os.environ.get``) that would
    pass the blank value through.
    """
    monkeypatch.setenv("PAPERLESS_MCP_SERVER_NAME", "   ")
    monkeypatch.setenv("PAPERLESS_MCP_INSTRUCTIONS", "   ")
    server = make_server()
    assert server.name == "paperless-mcp"
    assert (server.instructions or "").startswith(
        "paperless-mcp: Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.",
    )


def test_no_file_exchange_scaffolding(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The removed exchange-directory setting cannot enable transfer tools.

    Current Path 1 transfers reuse the generic names but require BASE_URL.
    MCP_EXCHANGE_DIR alone must never activate the old file-exchange surface.
    """
    monkeypatch.setenv("PAPERLESS_MCP_TRANSPORT", "http")
    monkeypatch.delenv("PAPERLESS_MCP_BASE_URL", raising=False)
    monkeypatch.setenv("MCP_EXCHANGE_DIR", str(tmp_path))

    server = make_server(transport="http")

    async def _list_tools() -> set[str]:
        async with Client(server) as smoke_client:
            return {t.name for t in await smoke_client.list_tools()}

    tools = asyncio.run(_list_tools())
    assert "create_download_link" not in tools
    assert "fetch_file" not in tools
    assert "create_upload_link" not in tools


def test_all_tools_registered() -> None:
    """make_server() exposes every Paperless tool via list_tools()."""
    server = make_server()

    async def _list_tools() -> set[str]:
        async with Client(server) as smoke_client:
            return {t.name for t in await smoke_client.list_tools()}

    names = asyncio.run(_list_tools())
    assert len(names) >= 49
    assert "create_download_link" not in names
    for expected in ("list_documents", "create_tag", "wait_for_task", "get_statistics"):
        assert expected in names, f"missing tool: {expected}"


def test_tool_allowlist_hides_unlisted_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Operator tool visibility limits both listings and invocation surfaces.

    This is the supported way to run a read-only instance, so the assertion
    that a write tool is unreachable is the contract an operator relies on.
    """
    from fastmcp.exceptions import ToolError

    monkeypatch.setenv("PAPERLESS_MCP_TOOLS_ALLOW", "list_documents")
    server = make_server()

    async def _probe() -> set[str]:
        async with Client(server) as smoke_client:
            tools = {t.name for t in await smoke_client.list_tools()}
            with pytest.raises(ToolError, match=r"Unknown tool: 'create_tag'"):
                await smoke_client.call_tool("create_tag", {})
            return tools

    assert asyncio.run(_probe()) == {"list_documents"}
