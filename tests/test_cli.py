"""CLI tests for Paperless MCP.

Uses the standard typer ``CliRunner`` pattern: ``--help`` exits via
typer before any command body runs, so these tests don't import
``server.py`` or start uvicorn — keeping them fast and free of side
effects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner, Result

from paperless_mcp.cli import app

if TYPE_CHECKING:
    from fastmcp_pvl_core import ServerConfig

_ENV_PREFIX = "PAPERLESS_MCP"


def _invoke_http(*args: str) -> tuple[Result, dict[str, object]]:
    """Invoke HTTP serve with every blocking side effect patched."""
    captured: dict[str, object] = {}

    def fake_run_http(
        _asgi_app: object,
        *,
        config: ServerConfig,
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        captured["host"] = config.host if host is None else host
        captured["port"] = config.port if port is None else port

    fake_server = MagicMock()
    fake_server.http_app.return_value = MagicMock()

    with (
        patch("paperless_mcp.cli.run_http", side_effect=fake_run_http),
        patch("paperless_mcp.server.make_server", return_value=fake_server),
        patch("paperless_mcp.cli.build_event_store", return_value=MagicMock()),
    ):
        result = CliRunner().invoke(
            app,
            ["serve", "--transport", "http", *args],
        )
    return result, captured


def test_help_exits_zero() -> None:
    """`paperless-mcp --help` lists the serve command."""
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "serve" in result.output


def test_serve_help_exits_zero() -> None:
    """`paperless-mcp serve --help` documents the transport flag."""
    result = CliRunner().invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "stdio" in result.output


def test_no_args_shows_help() -> None:
    """Bare invocation shows help text via ``no_args_is_help=True``.

    Typer/Click exits with code 2 (missing command) but still prints the
    help output.  Pinning the exit code locks in the documented behaviour
    so a future typer version that routes bare invocation to a different
    code (e.g. 1 for runtime error) surfaces as a test failure.
    """
    result = CliRunner().invoke(app, [])
    assert result.exit_code == 2
    assert "serve" in result.output


def test_serve_http_passes_cli_bind_address() -> None:
    """Explicit HTTP host and port reach pvl-core's runner."""
    result, captured = _invoke_http("--host", "10.0.0.1", "--port", "7777")

    assert result.exit_code == 0, result.output
    assert captured == {"host": "10.0.0.1", "port": 7777}


def test_serve_reports_a_configuration_error_in_one_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A malformed operator value is one error line and exit 1."""
    monkeypatch.setenv(f"{_ENV_PREFIX}_PORT", "notanint")

    result = CliRunner().invoke(app, ["serve", "--transport", "http"])

    assert result.exit_code == 1
    assert "ERROR: configuration error:" in result.output
    assert f"{_ENV_PREFIX}_PORT" in result.output
    assert "Traceback" not in result.output
    assert "\u2502" not in result.output, "Rich traceback frame detected"
