"""Domain-specific configuration for paperless-mcp.

Kept separate from the template-owned :mod:`paperless_mcp.config` so that
``copier update`` remains conflict-free.  The template's ``config.py`` provides
``CONFIG-FIELDS-START`` sentinels for server-level domain fields; this module
handles Paperless-specific secrets and complex validation via pydantic-settings.
"""

from __future__ import annotations

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PREFIX = "PAPERLESS_MCP_"


class DomainConfig(BaseSettings):
    """Paperless-specific runtime configuration loaded from env vars.

    Attributes:
        paperless_url: Base URL of the Paperless-NGX REST API, without a
            trailing slash.
        api_token: Paperless service-account token used for every outbound
            request.  Stored as :class:`~pydantic.SecretStr` so it never
            appears in ``repr()`` or serialised config snapshots.
        http_timeout_seconds: Per-request HTTP timeout.  Applies to connect,
            read, write, and pool independently.
        http_retries: Retries (not counting the initial attempt) for
            idempotent requests on network errors or ``5xx`` responses.
        download_link_ttl_seconds: Time-to-live of download URLs issued by
            the ``create_download_link`` tool.  Clamped ``[30, 3600]``.
        default_page_size: Default ``page_size`` parameter for list tools.
            Clamped ``[1, 100]``.
    """

    model_config = SettingsConfigDict(
        env_prefix=_ENV_PREFIX,
        case_sensitive=False,
        extra="ignore",
    )

    paperless_url: str = Field(..., min_length=1)
    api_token: SecretStr = Field(...)
    http_timeout_seconds: float = Field(default=30.0, gt=0, le=600)
    http_retries: int = Field(default=2, ge=0, le=10)
    download_link_ttl_seconds: int = Field(default=300, ge=30, le=3600)
    default_page_size: int = Field(default=25, ge=1, le=100)

    @field_validator("paperless_url")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")


def load_domain_config() -> DomainConfig:
    """Load :class:`DomainConfig` from environment, raising ``ValueError``.

    Re-raises pydantic ``ValidationError`` as ``ValueError``.  For missing
    required fields the message includes the env var name (e.g.
    ``PAPERLESS_MCP_PAPERLESS_URL``) so callers get actionable guidance.
    """
    try:
        return DomainConfig()  # type: ignore[call-arg]
    except ValidationError as exc:
        parts: list[str] = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            if error["type"] == "missing":
                env_var = _ENV_PREFIX + field.upper()
                parts.append(f"{env_var}: {error['msg']}")
            else:
                parts.append(f"{field}: {error['msg']}")
        raise ValueError("; ".join(parts)) from exc
