"""Configuration for Paperless MCP.

Composes :class:`fastmcp_pvl_core.ServerConfig` via the domain
:class:`ProjectConfig` dataclass — never inherits.

Add domain-specific fields between the CONFIG-FIELDS sentinels; copier
update preserves that block across template updates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fastmcp_pvl_core import (
    ServerConfig,
    TransferConfig,
    env,  # noqa: F401  — re-exported so CONFIG-FROM-ENV additions don't need a new import
)

_ENV_PREFIX = "PAPERLESS_MCP"


@dataclass(frozen=True)
class ProjectConfig:
    """Domain config for Paperless MCP.  Compose — don't inherit."""

    server: ServerConfig = field(default_factory=ServerConfig)

    # CONFIG-FIELDS-START — add domain fields below; kept across copier update
    transfer: TransferConfig = field(default_factory=TransferConfig)
    # CONFIG-FIELDS-END

    @classmethod
    def from_env(cls) -> ProjectConfig:
        """Load :class:`ProjectConfig` from ``PAPERLESS_MCP_*`` env vars."""
        return cls(
            server=ServerConfig.from_env(_ENV_PREFIX),
            # CONFIG-FROM-ENV-START — populate domain fields below; kept across copier update
            transfer=TransferConfig.from_env(_ENV_PREFIX),
            # CONFIG-FROM-ENV-END
        )
