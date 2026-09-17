"""Domain layer for paperless-mcp: the Paperless client lifecycle and re-exports.

The template's ``_server_deps.server_lifespan`` (template-owned) constructs a
:class:`Service` here on startup and stops it on shutdown.  Tool and resource
registration happens before the lifespan runs, so the shared
:class:`~paperless_mcp.tools._context.ToolContext` is built eagerly at
registration time and staged in a module-level slot; :meth:`Service.start`
adopts it so :meth:`Service.stop` can close the HTTP client.

:func:`tool_context_for` keys that slot on the server it was built for, so
``register_tools`` and ``register_resources`` share one client whichever of
them runs first.  The order is decided in template-owned ``server.py``, which
a ``copier update`` re-renders, so it is not an invariant this package can
rely on.

:func:`build_tool_context` takes a :class:`~paperless_mcp.config.ProjectConfig`
and reads no environment of its own; :func:`tool_context_for` falls back to
``ProjectConfig.from_env()`` when no config is handed to it.  It has to: the
template's ``make_server`` calls ``register_tools(mcp)`` with no config, and
its ``DOMAIN-WIRING`` block — the one place this project may add a call — runs
*after* registration, while ``default_page_size`` is a tool parameter default
baked into the schema *during* registration.  So a config passed to
``make_server(config=...)`` still does not reach the Paperless client; that is
unchanged from v1.0.2 and tracked at pvliesdonk/fastmcp-server-template#622.

The slot holds one entry.  Staging a second server's context over an
unadopted first closes the first one's client on the way out, so a process
that builds servers it never enters — a test suite, mostly — does not
accumulate them.

Importers that need a typed Paperless client can do::

    from paperless_mcp.domain import PaperlessClient

instead of reaching into ``paperless_mcp.client`` directly.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from fastmcp_pvl_core import InstructionRole, instructions_for

from paperless_mcp.client import (
    AuthError,
    ConflictError,
    NotFoundError,
    PaperlessAPIError,
    PaperlessClient,
    RateLimitError,
    UpstreamError,
    ValidationError,
)
from paperless_mcp.config import _ENV_PREFIX, ProjectConfig

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastmcp import FastMCP

    from paperless_mcp.tools._context import ToolContext

logger = logging.getLogger(__name__)

__all__ = [
    "AuthError",
    "ConflictError",
    "NotFoundError",
    "PaperlessAPIError",
    "PaperlessClient",
    "RateLimitError",
    "Service",
    "UpstreamError",
    "ValidationError",
    "add_instance_instructions",
    "build_tool_context",
    "pending_tool_context",
    "tool_context_for",
    "upstream_version_provider",
]

_pending: tuple[object, ToolContext] | None = None


def build_tool_context(config: ProjectConfig) -> ToolContext:
    """Build a :class:`ToolContext` — and its Paperless client — from *config*.

    Reads no environment: everything it needs is already on *config*.  The
    caller decides where that config came from, which is what makes the
    context constructible in a test without touching ``os.environ``.

    Args:
        config: The resolved project config.

    Returns:
        A context holding a fresh :class:`PaperlessClient`.  The caller owns
        closing it (:meth:`Service.stop` does, for the staged one).

    Raises:
        ValueError: If the Paperless URL or the API token is unset.  This is
            the server's fail-fast startup contract: registration is the first
            thing ``make_server`` does that needs a client, so an operator who
            forgot either variable is told which one by name.
    """
    from paperless_mcp.tools._context import ToolContext

    missing = [
        name
        for name, value in (
            (f"{_ENV_PREFIX}_PAPERLESS_URL", config.paperless_url),
            (f"{_ENV_PREFIX}_API_TOKEN", config.api_token),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            f"{', '.join(missing)}: required but not set. Set "
            f"{_ENV_PREFIX}_PAPERLESS_URL to your Paperless-NGX API base URL "
            f"and {_ENV_PREFIX}_API_TOKEN to a service-account token."
        )

    client = PaperlessClient(
        base_url=config.paperless_url,
        api_token=config.api_token,
        timeout_seconds=config.http_timeout_seconds,
        max_retries=config.http_retries,
    )
    return ToolContext(
        client=client,
        default_page_size=config.default_page_size,
        public_url=config.public_url,
    )


def tool_context_for(mcp: object, config: ProjectConfig | None = None) -> ToolContext:
    """Return the shared :class:`ToolContext` for *mcp*, building it once.

    The first registrar to ask builds the Paperless client and stages the
    context against *mcp*; the second gets the same object back rather than
    opening a second HTTP client. Staging is what lets :class:`Service`, which
    the lifespan constructs long after registration, close that client.

    Args:
        mcp: The server being registered on, used only as an identity so a
            second server does not adopt the first one's client.
        config: The config to build from.  ``None`` reads the environment via
            ``ProjectConfig.from_env()`` — the only thing available to a
            registrar the template calls with no config.  Ignored when a
            context is already staged for *mcp*: the first registrar's config
            wins, so the two registrars cannot disagree about page size.

    Returns:
        The context for *mcp*, freshly built or the already-staged one.
    """
    global _pending
    if _pending is not None:
        if _pending[0] is mcp:
            return _pending[1]
        _discard(_pending[1])
        _pending = None

    context = build_tool_context(config or ProjectConfig.from_env())
    _pending = (mcp, context)
    return context


def _discard(context: ToolContext) -> None:
    """Close a staged context that no lifespan will ever adopt.

    Server construction is synchronous — pvl-core finalises the composed
    instructions during it and refuses to do that inside a running loop — so
    there is normally no loop here and the close completes. If there is one,
    closing would mean blocking it, so the client is dropped instead: it opens
    no sockets until its first request, and a context nothing adopted never
    makes one.

    Args:
        context: The staged context being replaced.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(context.client.aclose())
        logger.debug("unadopted_tool_context_closed")
    else:
        logger.debug("unadopted_tool_context_dropped reason=running_event_loop")


def pending_tool_context() -> ToolContext | None:
    """Return the context staged by :func:`tool_context_for`, if any.

    Returns:
        The staged context, or ``None`` when nothing is staged.
    """
    return _pending[1] if _pending is not None else None


def upstream_version_provider(
    mcp: object,
) -> Callable[[], Awaitable[dict[str, object] | None]]:
    """Build the zero-arg provider ``register_server_info_tool`` calls.

    Captures the :class:`ToolContext` staged for *mcp* — the same one the tool
    registrars and :class:`Service` share — so asking ``get_server_info`` for
    the Paperless version reuses the open HTTP client instead of opening a
    second one.

    The version reported is the one *installed on the connected instance*
    (``SystemClient.installed_version``), not the newest release published
    upstream.  The distinction is the whole point of the block: the question
    it answers is "which Paperless am I talking to", and Paperless's
    ``/api/remote_version/`` answers a different one — see
    :class:`~paperless_mcp.models.system.RemoteVersion`.  Whether an update
    exists stays the ``get_remote_version`` tool's job; reporting both from
    one field is what made the first version of this provider wrong.

    Called from ``make_server``'s ``DOMAIN-WIRING`` block, which runs *after*
    ``register_server_info_tool``; the ``upstream_version=`` keyword there is a
    lambda, so the name this returns is looked up when the tool is called, by
    which time the block has bound it.

    Args:
        mcp: The server whose staged context the provider should use.

    Returns:
        An async zero-arg callable returning ``{"version": <installed>}``, or
        ``None`` when Paperless cannot answer.  One HTTP request per call.
    """
    context = tool_context_for(mcp)

    async def _paperless_version() -> dict[str, object] | None:
        """Report the installed Paperless-NGX version, or ``None``.

        Returns:
            ``{"version": <the version running on the connected instance>}``,
            or ``None`` — never raises.  The version is optional enrichment of
            a tool whose primary job is reporting *this* server's build, so an
            unreachable Paperless must not fail the call.  ``None`` also covers
            a token without ``documents.view_uisettings``, which Paperless
            answers ``403`` to; see
            :meth:`~paperless_mcp.client.system.SystemClient.installed_version`.
        """
        try:
            installed = await context.client.system.installed_version()
        except (PaperlessAPIError, ValueError):
            # ValueError covers a malformed body: both json.JSONDecodeError and
            # pydantic's ValidationError derive from it.
            logger.debug("upstream_version_unavailable label=paperless", exc_info=True)
            return None
        return {"version": installed}

    return _paperless_version


def add_instance_instructions(mcp: FastMCP, config: ProjectConfig) -> None:
    """Tell the model which Paperless instance this server fronts.

    Without this the composed instructions are the identity line and the
    documentation pointer, so a model handed a link such as
    ``https://paperless.example.org/documents/42/`` in conversation has no
    stated basis for recognising it as *this* server's instance, and the
    ``paperless://`` resource URIs are described nowhere it reads before its
    first call.  The server already knows the URL — tool results build
    ``web_url`` and ``share_url`` from the same :attr:`ProjectConfig.public_url`
    — so stating it costs the operator nothing, where
    ``PAPERLESS_MCP_INSTANCE_DESCRIPTION`` would have them retype it by hand.

    One ``CAPABILITIES`` snippet rather than two, and no ``requires_tools``:

    * The URL alone would fit ``INSTANCE`` better, but it is only *useful*
      together with the mapping from a link to an id and a resource URI, and
      splitting the two across roles puts the operator's ``POLICY`` text
      between the halves (``_ROLE_ORDER`` runs INSTANCE, POLICY, CAPABILITIES).
    * ``requires_tools`` gates on tool names, and half of what this snippet
      describes is resources, which the operator visibility rule does not touch
      at all.  Naming one tool would drop the instance URL for an operator who
      merely hid that tool, so the prose says "the document tools" instead.

    Called from ``make_server``'s ``DOMAIN-WIRING`` block, which runs before
    ``finalize_instructions`` renders the builder.

    Args:
        mcp: The server whose instruction builder receives the snippet.
        config: The resolved project config, read for
            :attr:`~paperless_mcp.config.ProjectConfig.public_url`.
    """
    url = config.public_url
    if not url:
        # Only reachable through a hand-built ``ProjectConfig()``: the config
        # the server runs on cannot get this far without a URL, because
        # ``build_tool_context`` refuses to register tools without one.
        logger.debug("instance_instructions_skipped reason=no_public_url")
        return

    instructions_for(mcp).add(
        f"This server fronts the Paperless-NGX instance at {url}. "
        f"A link of the form {url}/documents/<id>/ is a document on it: pass "
        "<id> to the document tools, or read paperless://documents/<id> "
        "(also /content, /metadata, /notes, /history, /thumbnail, /preview, "
        "/download). Collections read as <name>://paperless, "
        "for example tags://paperless.",
        role=InstructionRole.CAPABILITIES,
    )


class Service:
    """Owns the staged Paperless client for the duration of the server lifespan."""

    def __init__(self) -> None:
        self._ready = False
        self._context: ToolContext | None = None

    async def start(self) -> None:
        """Adopt the staged tool context; the lifespan now owns its client.

        Takes whatever is staged without checking which server it was built
        for. That the two agree is an assumption, not something this method
        can enforce: ``_server_deps.server_lifespan`` is template-owned, and it
        constructs ``Service()`` and calls ``start()`` with no arguments, so
        the server whose lifespan is starting is not in scope here. Checking
        would mean editing a template-owned file, which is the drift this
        module exists to avoid.

        The assumption holds by construction — ``make_server`` registers tools
        and resources for a server immediately before that server's lifespan is
        entered, so the slot holds that server's context and nothing else's —
        and :func:`tool_context_for` closes any context it displaces, so a
        mismatch cannot silently outlive its server either.
        """
        global _pending
        self._context = pending_tool_context()
        _pending = None
        self._ready = True

    async def stop(self) -> None:
        """Close the Paperless HTTP client this service adopted."""
        if self._context is not None:
            await self._context.client.aclose()
            logger.info("client_closed")
        self._context = None
        self._ready = False

    async def ping(self) -> str:
        """Answer a liveness probe.

        Returns:
            ``"pong"`` once the lifespan has started, ``"not ready"`` before.
        """
        return "pong" if self._ready else "not ready"

    async def status(self) -> dict[str, object]:
        """Report the service's readiness.

        Returns:
            A mapping with a single ``ready`` key.
        """
        return {"ready": self._ready}
