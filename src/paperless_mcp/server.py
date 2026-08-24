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
    configure_logging_from_env,
    register_transfer_routes,
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
from paperless_mcp.tools._transfer_sink import PaperlessTransferSink

logger = logging.getLogger(__name__)

_ENV_PREFIX = "PAPERLESS_MCP"


def make_server(
    *,
    transport: str = "stdio",
    config: ProjectConfig | None = None,
) -> FastMCP:
    """Construct the Paperless MCP FastMCP server.

    Args:
        transport: ``"stdio"`` / ``"http"`` / ``"sse"``.  HTTP-only
            features (download links) are wired only when transport
            != ``"stdio"`` and ``PAPERLESS_MCP_BASE_URL`` is set.
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
        "Server config: version=%s name=paperless-mcp auth=%s",
        pkg_ver,
        auth_mode,
    )

    mcp = FastMCP(
        name="paperless-mcp",
        instructions=build_instructions(
            env_prefix=_ENV_PREFIX,
            domain_line="Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.",
        ),
        lifespan=_lifespan,
        auth=auth,
    )

    wire_middleware_stack(mcp)

    register_tools(mcp, _tool_ctx)
    register_resources(mcp, _tool_ctx)
    register_prompts(mcp)
    register_apps(mcp)

    # One-time capability-link downloads via pvl-core's Transfer API. HTTP-only
    # (the /transfer/{token} route needs an HTTP server) and only with base_url
    # set, since register_transfer_routes raises without a public base URL —
    # gate on both so a stdio or unconfigured deployment simply omits the
    # feature rather than failing to start. create_upload_link has no matching
    # Paperless write operation (upload_document already covers ingestion with
    # real metadata), so it's removed right after registration.
    if transport != "stdio" and config.server.base_url:
        transfer_sink = PaperlessTransferSink(_client)
        register_transfer_routes(
            mcp,
            config.server,
            config.transfer,
            sink=transfer_sink,
            validate=transfer_sink.validate,
            download_note=(
                'For this server, ref is a document ID (e.g. "982"), optionally '
                'suffixed with ":archived" or ":preview" to select a variant '
                "other than the original file."
            ),
        )
        mcp.local_provider.remove_tool("create_upload_link")

    return mcp
