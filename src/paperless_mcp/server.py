"""Paperless MCP — FastMCP server entry point.

Composes the primitives from ``fastmcp-pvl-core`` into a
project-specific ``make_server()``.  See
https://gofastmcp.com/servers for the FastMCP server surface and
``fastmcp-pvl-core``'s README for the composable helpers used below.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Any

from fastmcp import FastMCP
from fastmcp_pvl_core import (
    ServerConfig,  # noqa: F401  — re-exported for downstream projects' convenience
    build_auth,
    build_event_store,  # noqa: F401  — re-exported for downstream projects' convenience
    build_instructions,
    build_kv_store,  # noqa: F401  — re-exported for downstream projects' convenience
    configure_logging_from_env,
    env,
    register_server_info_tool,
    resolve_auth_mode,
    wire_middleware_stack,
)

from paperless_mcp._domain_config import load_domain_config
from paperless_mcp._server_apps import register_apps
from paperless_mcp._server_deps import server_lifespan
from paperless_mcp.client import PaperlessClient
from paperless_mcp.config import ProjectConfig
from paperless_mcp.prompts import register_prompts
from paperless_mcp.resources import register_resources
from paperless_mcp.tools import register_tools
from paperless_mcp.tools._context import ToolContext

logger = logging.getLogger(__name__)

_ENV_PREFIX = "PAPERLESS_MCP"


def make_server(
    *,
    transport: str = "stdio",
    config: ProjectConfig | None = None,
) -> FastMCP:
    """Construct the Paperless MCP FastMCP server.

    Args:
        transport: ``"stdio"`` / ``"http"`` / ``"sse"``.  Gates any
            transport-specific wiring added in the DOMAIN-WIRING block
            (e.g. HTTP-only custom routes, which cannot be served under
            stdio) and appears as ``transport=%s`` in the startup log.
        config: Optional pre-loaded config; default loads from env.

    Returns:
        A configured :class:`fastmcp.FastMCP` instance.
    """
    config = config or ProjectConfig.from_env()
    configure_logging_from_env()

    domain_cfg = load_domain_config()
    _client = PaperlessClient(
        base_url=domain_cfg.paperless_url,
        api_token=domain_cfg.api_token.get_secret_value(),
        timeout_seconds=domain_cfg.http_timeout_seconds,
        max_retries=domain_cfg.http_retries,
    )
    _tool_ctx = ToolContext(
        client=_client,
        read_only=False,
        default_page_size=domain_cfg.default_page_size,
        public_url=domain_cfg.public_url,
    )

    @asynccontextmanager
    async def _lifespan(mcp_arg: object) -> AsyncIterator[dict[str, Any]]:
        async with server_lifespan(mcp_arg) as state:
            try:
                yield state
            finally:
                await _client.aclose()
                logger.info("client_closed")

    # Operator overrides: SERVER_NAME renames this instance; INSTRUCTIONS
    # replaces the default instructions text (the latter is the override that
    # build_instructions' hint advertises). Both fall back when unset/empty.
    server_name = env(_ENV_PREFIX, "SERVER_NAME", "paperless-mcp")
    instructions = env(_ENV_PREFIX, "INSTRUCTIONS") or build_instructions(
        env_prefix=_ENV_PREFIX,
        domain_line="Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.",
    )

    auth = build_auth(config.server)
    auth_mode = resolve_auth_mode(config.server) if auth is not None else "none"
    if auth_mode == "none":
        logger.warning(
            "No auth configured — server accepts unauthenticated connections"
        )
    else:
        logger.info("Auth enabled: mode=%s", auth_mode)

    try:
        pkg_ver = _pkg_version("pvliesdonk-paperless-mcp")
    except PackageNotFoundError:
        pkg_ver = "unknown"

    logger.info(
        "Server config: version=%s name=%s transport=%s auth=%s",
        pkg_ver,
        server_name,
        transport,
        auth_mode,
    )

    mcp = FastMCP(
        name=server_name,
        instructions=instructions,
        lifespan=_lifespan,
        auth=auth,
    )

    wire_middleware_stack(mcp)

    register_tools(mcp, _tool_ctx)
    register_resources(mcp, _tool_ctx)
    register_prompts(mcp)
    register_apps(mcp)

    register_server_info_tool(
        mcp,
        server_name=server_name,
        server_version=pkg_ver,
        # DOMAIN-UPSTREAM-START — wire upstream version reporting for servers
        # that talk to a remote service (paperless-mcp, etc.). The provider is
        # a zero-arg callable; the simplest pattern is a module-level upstream
        # client (typically constructed from env vars at import time) whose
        # version method is referenced here. ``CurrentContext()`` is a FastMCP
        # DI marker — it only resolves to a live context when used as a
        # parameter default in a tool/resource handler, so it cannot be called
        # directly from a zero-arg provider.
        # Uncomment the kwargs below as additional arguments to this call:
        # upstream_version=lambda: _upstream_client.remote_version(),
        # upstream_label="paperless",
        # DOMAIN-UPSTREAM-END
    )

    # DOMAIN-WIRING-START — project-specific wiring (custom HTTP routes,
    # transforms, mode toggles, alternative middleware, additional registrations);
    # kept across copier update. Leave empty for projects that don't customise
    # make_server() beyond the standard scaffold.
    # DOMAIN-WIRING-END

    return mcp
