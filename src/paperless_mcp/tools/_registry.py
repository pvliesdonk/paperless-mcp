"""Helpers for registering MCP tools with icons, annotations, and read-only gating.

These are local utilities pending fastmcp-pvl-core#16 for upstream versions.

The helper looks up icons and annotations from per-tool registries by tool
name, so call sites stay compact: ``@register_tool(mcp, "list_tags",
read_only_mode=read_only)``.
"""

from __future__ import annotations

import base64
import functools
import logging
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp.types import Icon
from pydantic import ValidationError as PydanticValidationError

from paperless_mcp.client._errors import PaperlessAPIError, error_from_response

F = TypeVar("F", bound=Callable[..., object])


logger = logging.getLogger(__name__)


def _wrap_with_error_handling(name: str, func: F) -> F:
    # ``PaperlessHTTP`` normally maps non-2xx and network errors into
    # ``PaperlessAPIError`` before they reach us, so the two ``httpx.*``
    # branches below are defensive safety nets for any call path that
    # bypasses ``PaperlessHTTP._request`` (e.g. future one-off httpx calls).
    #
    # We raise ``ToolError`` rather than returning an error string: returning a
    # string conflicts with tools whose declared output schema is a typed model
    # (``Tag``, ``Paginated[Tag]``, ...). FastMCP would refuse to coerce the
    # string into ``structured_content``. Raising ``ToolError`` lets the MCP
    # layer emit a proper ``CallToolResult(isError=True)`` regardless of the
    # tool's output schema.
    @functools.wraps(func)
    async def wrapper(*args: object, **kwargs: object) -> object:
        try:
            return await func(*args, **kwargs)  # type: ignore[misc]
        except PaperlessAPIError as exc:
            logger.warning(
                "tool_api_error tool=%s status=%s msg=%s", name, exc.status_code, exc
            )
            raise ToolError(
                f"Paperless API error {exc.status_code}: {exc.detail}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            api_exc = error_from_response(exc.response)
            logger.warning(
                "tool_http_status_error tool=%s status=%s url=%s",
                name,
                api_exc.status_code,
                exc.request.url,
            )
            raise ToolError(
                f"Paperless API error {api_exc.status_code}: {api_exc.detail}"
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("tool_network_error tool=%s error=%s", name, exc)
            raise ToolError(f"Network error connecting to Paperless: {exc}") from exc
        except PydanticValidationError as exc:
            errors = exc.errors()
            detail = (
                errors[0].get("msg") or errors[0].get("type") or "unknown"
                if errors
                else "unknown"
            )
            logger.warning(
                "tool_validation_error tool=%s errors=%d", name, exc.error_count()
            )
            raise ToolError(
                f"Response validation failed ({exc.error_count()} error(s)): {detail}"
            ) from exc

    return wrapper  # type: ignore[return-value]


def load_svg_data_uri(path: Path) -> str:
    """Read an SVG file and return it as an ``image/svg+xml`` data URI."""
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_icon(path: Path) -> Icon:
    """Build an :class:`Icon` pointing at the given SVG file."""
    return Icon(src=load_svg_data_uri(path), mimeType="image/svg+xml")


def register_tool(
    mcp: FastMCP,
    name: str,
    *,
    read_only_mode: bool = False,
    **tool_kwargs: object,
) -> Callable[[F], F]:
    """Return a decorator that registers *func* as an MCP tool named *name*.

    Looks up icons from :data:`paperless_mcp.tools._icons.ICON_REGISTRY`
    and annotations from :data:`paperless_mcp.tools._annotations.ANNOTATION_REGISTRY`.

    When ``read_only_mode`` is ``True`` and the tool's ``readOnlyHint`` is
    ``False``, the decorator returns the function unchanged (no registration).

    Raises:
        KeyError: If *name* is not present in either registry.
    """
    from paperless_mcp.tools._annotations import ANNOTATION_REGISTRY
    from paperless_mcp.tools._icons import ICON_REGISTRY

    icons = ICON_REGISTRY[name]
    annotations = ANNOTATION_REGISTRY[name]
    read_only_tool = bool(annotations.get("readOnlyHint", False))

    def decorator(func: F) -> F:
        if read_only_mode and not read_only_tool:
            return func
        wrapped = _wrap_with_error_handling(name, func)
        return mcp.tool(  # type: ignore[call-overload, no-any-return]
            name=name,
            icons=icons,
            annotations=dict(annotations),
            **tool_kwargs,
        )(wrapped)

    return decorator
