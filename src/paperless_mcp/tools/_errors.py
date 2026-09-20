"""Paperless error translation independent of tool registration."""

from __future__ import annotations

import functools
import logging
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import httpx
from fastmcp.exceptions import ToolError
from pydantic import ValidationError as PydanticValidationError

from paperless_mcp.client._errors import PaperlessAPIError, error_from_response

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)


def paperless_errors(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Translate Paperless failures without registering or changing a tool.

    Args:
        func: Domain coroutine, wrapped inside any core execution decorator.

    Returns:
        A signature-preserving coroutine that raises MCP ToolError on failure.
    """
    name = func.__name__

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
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
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

    return wrapper
