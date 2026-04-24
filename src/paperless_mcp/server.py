"""Paperless MCP — FastMCP server entry point.

Composes the primitives from ``fastmcp-pvl-core`` into a
project-specific ``make_server()``.  See
https://gofastmcp.com/servers for the FastMCP server surface and
``fastmcp-pvl-core``'s README for the composable helpers used below.
"""

from __future__ import annotations

import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from fastmcp import FastMCP
from fastmcp_pvl_core import (
    ArtifactStore,
    ServerConfig,  # noqa: F401  — re-exported for downstream projects' convenience
    build_auth,
    build_event_store,  # noqa: F401  — re-exported for downstream projects' convenience
    build_instructions,
    configure_logging_from_env,
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
        transport: ``"stdio"`` / ``"http"`` / ``"sse"``.  HTTP-only
            features (artifact downloads) are wired only when transport
            != ``"stdio"``.
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
        "Server config: version=%s name=paperless-mcp auth=%s",
        pkg_ver,
        auth_mode,
    )

    mcp = FastMCP(
        name="paperless-mcp",
        instructions=build_instructions(
            read_only=True,
            env_prefix=_ENV_PREFIX,
            domain_line="Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.",
        ),
        lifespan=server_lifespan,
        auth=auth,
    )

    wire_middleware_stack(mcp)

    register_tools(mcp, _tool_ctx)
    register_resources(mcp, _tool_ctx)
    register_prompts(mcp)
    register_apps(mcp)

    if transport != "stdio":
        artifact_store = ArtifactStore(ttl_seconds=3600)
        ArtifactStore.register_route(mcp, artifact_store)

    return mcp
