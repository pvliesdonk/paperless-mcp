"""Configuration for Paperless MCP.

Composes :class:`fastmcp_pvl_core.ServerConfig` via the domain
:class:`ProjectConfig` dataclass — never inherits.

Add domain-specific fields between the CONFIG-FIELDS sentinels, populate
them in ``from_env`` between the CONFIG-FROM-ENV sentinels, and enforce
their invariants in ``__post_init__`` between the CONFIG-VALIDATE
sentinels; copier update preserves all three blocks across template
updates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fastmcp_pvl_core import (
    JobsConfig,
    ServerConfig,
    # Used by `_default_server_name` below, and re-exported so CONFIG-FROM-ENV
    # additions don't need a new import.  No `noqa: F401` — that factory makes
    # the import genuinely used, and a redundant directive fails RUF100.
    env,
)

_ENV_PREFIX = "PAPERLESS_MCP"


def _default_server_name() -> str:
    """``PAPERLESS_MCP_SERVER_NAME``, falling back to the project name.

    A module-level factory rather than a read inside `from_env`, for two
    reasons that both bite if it moves:

    - The generator AST-scans `ProjectConfig.from_env` for literal
      ``env(prefix, "SUFFIX")`` calls and turns each into a *domain* var.
      ``PAPERLESS_MCP_SERVER_NAME`` is already declared with template
      provenance in the template's `config-presentation.yml`, so a read in
      `from_env` would be discovered twice and fail generation with the
      duplicate-name error. `docs/design/config-migration.md` documents this
      case and prescribes exactly this workaround; the scan only walks
      `from_env`, so a module-level helper stays invisible to it.
    - As a ``default_factory`` the env read happens per construction, so
      ``ProjectConfig()`` still honours the environment while
      ``ProjectConfig(server_name=...)`` wins outright — which is the whole
      point of the field.
    """
    return env(_ENV_PREFIX, "SERVER_NAME", "paperless-mcp")


@dataclass(frozen=True)
class ProjectConfig:
    """Domain config for Paperless MCP.  Compose — don't inherit."""

    server: ServerConfig = field(default_factory=ServerConfig)

    # Template-owned, deliberately OUTSIDE the CONFIG-FIELDS sentinels: the
    # server's own name is part of the scaffold's contract with
    # `server.py`, which uses it for both `FastMCP(name=...)` and the shaped
    # instruction identity so the two cannot disagree.  Do not redeclare it
    # inside the block below.
    server_name: str = field(default_factory=_default_server_name)

    # CONFIG-FIELDS-START — add domain fields below; kept across copier update
    #
    # One flat field per Paperless env var, named exactly after the var's
    # suffix, so the config-surface generator pairs each field's metadata with
    # the matching literal ``env(...)`` read in ``from_env``.  ``paperless_url``
    # and ``api_token`` are required in practice — ``build_tool_context``
    # refuses to build a Paperless client without them — but they still carry a
    # default here, because the template's own config-contract tests construct
    # ``ProjectConfig()`` with no arguments and a field without a default makes
    # that a ``TypeError``.  Their help text carries the requirement instead
    # (pvliesdonk/fastmcp-server-template#621).
    #
    # SPIKE (#110): composed, not inherited — same rule as `server` above. It
    # lives inside the domain block because the template does not wire jobs.
    # Holding it here is also what is meant to put the PAPERLESS_MCP_JOBS_*
    # vars in front of the config-surface generator: `server_config_surface()`
    # covers ServerConfig only.
    jobs: JobsConfig = field(default_factory=JobsConfig)
    paperless_url: str = field(
        default="",
        metadata={
            "help": (
                "Base URL of the Paperless-NGX REST API, without a trailing "
                "slash. The server refuses to start without it."
            ),
            "tags": ("paperless", "readme"),
            "wizard": {"group": "Paperless"},
        },
    )
    # ``repr=False``: this used to be a ``pydantic.SecretStr``, whose ``repr``
    # showed ``**********``.  A plain dataclass field would print the token in
    # every ``repr(config)``, so the exclusion is what keeps the old guarantee.
    api_token: str = field(
        default="",
        repr=False,
        metadata={
            "help": (
                "Paperless service-account token used for outbound API "
                "requests. The server refuses to start without it."
            ),
            "tags": ("paperless", "readme"),
            "wizard": {"group": "Paperless", "secret": True},
        },
    )
    http_timeout_seconds: float = field(
        default=30.0,
        metadata={
            "help": "Per-request HTTP timeout in seconds.",
            "tags": ("paperless",),
            "wizard": {"group": "Paperless"},
        },
    )
    http_retries: int = field(
        default=2,
        metadata={
            "help": (
                "Retries for idempotent requests after network errors or 5xx responses."
            ),
            "tags": ("paperless",),
            "wizard": {"group": "Paperless"},
        },
    )
    default_page_size: int = field(
        default=25,
        metadata={
            "help": "Default page size for list tools, from 1 through 100.",
            "tags": ("paperless",),
            "wizard": {"group": "Paperless"},
        },
    )
    # Annotated optional, but never ``None`` after ``__post_init__``, which
    # falls it back to ``paperless_url``.  The annotation is what the generator
    # reads to document the var as optional with no default of its own, so it
    # stays as declared; read the value through ``public_url`` below.
    paperless_public_url: str | None = field(
        default=None,
        metadata={
            "help": (
                "Public Paperless UI URL for user-visible links; defaults to "
                "PAPERLESS_URL."
            ),
            "tags": ("paperless", "readme"),
            "wizard": {"group": "Paperless"},
        },
    )

    @property
    def public_url(self) -> str:
        """Public-facing Paperless URL, falling back to :attr:`paperless_url`.

        ``__post_init__`` already resolves the fallback, so this only restates
        the guarantee as a plain ``str`` and spares callers a narrowing guard.

        Returns:
            The public Paperless UI base URL, without a trailing slash.
        """
        return self.paperless_public_url or self.paperless_url

    # CONFIG-FIELDS-END

    def __post_init__(self) -> None:
        """Validate composed domain fields.  Raise ``ValueError`` when invalid.

        Runs on EVERY construction path — ``from_env`` and a direct
        ``ProjectConfig(field=...)`` alike.  That is what makes this the right
        home for a field invariant: ``env_float`` / ``env_int`` bounds check
        only the *env-sourced* value, never the default, so a direct
        construction slips past them.  They also cannot express an exclusive
        bound (their ``minimum`` / ``maximum`` are inclusive, so "must be > 0"
        lets ``0`` through) or a cross-field rule (A requires B,
        mutually-exclusive pairs).  All three belong here.

        The dataclass is ``frozen=True``: read fields freely, but plain
        assignment raises.  To *normalise* rather than merely check, use
        ``object.__setattr__(self, "name", value)``.
        """
        # CONFIG-VALIDATE-START — validate domain fields below; kept across copier update
        # Normalise first, then check.  The dataclass is frozen, so both halves
        # go through ``object.__setattr__``.  This runs on ``from_env`` and on a
        # direct ``ProjectConfig(...)`` alike, which is why the bounds live here
        # rather than on the ``env_*`` readers.
        object.__setattr__(self, "paperless_url", self.paperless_url.rstrip("/"))
        object.__setattr__(
            self,
            "paperless_public_url",
            (self.paperless_public_url or "").rstrip("/") or self.paperless_url,
        )
        if not 0 < self.http_timeout_seconds <= 600:
            raise ValueError(
                f"{_ENV_PREFIX}_HTTP_TIMEOUT_SECONDS must be > 0 and <= 600, "
                f"got {self.http_timeout_seconds}"
            )
        if not 0 <= self.http_retries <= 10:
            raise ValueError(
                f"{_ENV_PREFIX}_HTTP_RETRIES must be >= 0 and <= 10, "
                f"got {self.http_retries}"
            )
        if not 1 <= self.default_page_size <= 100:
            raise ValueError(
                f"{_ENV_PREFIX}_DEFAULT_PAGE_SIZE must be >= 1 and <= 100, "
                f"got {self.default_page_size}"
            )
        # CONFIG-VALIDATE-END

    @classmethod
    def from_env(cls) -> ProjectConfig:
        """Load :class:`ProjectConfig` from ``PAPERLESS_MCP_*`` env vars."""
        return cls(
            server=ServerConfig.from_env(_ENV_PREFIX),
            # CONFIG-FROM-ENV-START — populate domain fields below; kept across copier update
            # Every read is a literal ``env(prefix, "SUFFIX")`` call so the
            # generator's AST scan can see it.  ``env_int`` / ``env_float`` are
            # not imported by the template's own import block, and adding them
            # would be an edit outside every sentinel, so the numeric reads are
            # parsed inline; their bounds are enforced in ``__post_init__``.
            paperless_url=env(_ENV_PREFIX, "PAPERLESS_URL") or "",
            api_token=env(_ENV_PREFIX, "API_TOKEN") or "",
            http_timeout_seconds=float(
                env(_ENV_PREFIX, "HTTP_TIMEOUT_SECONDS") or 30.0
            ),
            http_retries=int(env(_ENV_PREFIX, "HTTP_RETRIES") or 2),
            default_page_size=int(env(_ENV_PREFIX, "DEFAULT_PAGE_SIZE") or 25),
            paperless_public_url=env(_ENV_PREFIX, "PAPERLESS_PUBLIC_URL"),
            # SPIKE (#110): not a literal ``env(prefix, "SUFFIX")`` call, so
            # whether the generator's AST scan sees the JOBS_* vars at all is
            # exactly what running ``gen_config_surface.py --check`` decides.
            jobs=JobsConfig.from_env(_ENV_PREFIX),
            # CONFIG-FROM-ENV-END
        )
