"""Paperless error translation independent of tool registration.

Every Paperless failure is classified by who has to act on it, following the
``designing-tool-outcomes`` skill (the table is recorded in
``docs/design/tool-outcomes.md``):

- the model, by changing the request (400, 403, 404, other 4xx) or by
  re-reading first (409): a ``ToolError`` at INFO naming the next call;
- nobody, because it heals itself (429, 5xx, network): WARNING, "retry later";
- an operator (401, a response this server cannot parse): ERROR, "tell the
  user".

The message is written to the model; Paperless's own detail goes into it only
where it names what the model sent wrong, and into the log otherwise.
"""

from __future__ import annotations

import functools
import inspect
import logging
import reprlib
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import NoReturn, ParamSpec, TypeVar

import httpx
from fastmcp.exceptions import ToolError
from pydantic import ValidationError as PydanticValidationError

from paperless_mcp.client._bulk_objects import OBJECT_BULK_PARAMETERS
from paperless_mcp.client._errors import PaperlessAPIError, error_from_response

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)

_RETRY_LATER = (
    "The request was fine; retry in a minute, and tell the user if it keeps failing."
)
_TELL_USER = "The request was fine; tell the user, since retrying will not help."

# Where the model looks up each kind of id a tool takes, for the 404 message.
_LOOKUP_BY_ARG = {
    "document_id": "search_documents",
    "ref.document_id": "search_documents",
    "more_like": "search_documents",
    "tag_id": "list_tags",
    "correspondent_id": "list_correspondents",
    "document_type_id": "list_document_types",
    "field_id": "list_custom_fields",
    "storage_path_id": "list_storage_paths",
    "view_id": "list_saved_views",
    "share_link_id": "list_share_links",
    "note_id": "get_document_notes",
    "task_uuid": "list_tasks",
}
# A bulk tool's ``ids`` name objects of the kind the tool edits.
_LOOKUP_BY_TOOL = {
    "bulk_edit_documents": "search_documents",
    "bulk_edit_tags": "list_tags",
    "bulk_edit_correspondents": "list_correspondents",
    "bulk_edit_document_types": "list_document_types",
}
_DETAIL_MAX = 240


@dataclass(frozen=True)
class Outcome:
    """What the model is told about a failed call, and at which log level."""

    message: str
    log_level: int


def _transient(tool: str) -> Outcome:
    return Outcome(
        f"Paperless is unavailable or busy, so {tool} did not complete. "
        + _RETRY_LATER,
        logging.WARNING,
    )


def _detail(raw: str) -> str:
    """Paperless's own reason, cleaned for the model; empty when unusable.

    An HTML page (a proxy's error page) says nothing the model can act on, and
    a long body would crowd out the next step, so both are cut here; the full
    text is still logged where an operator needs it.
    """
    text = " ".join(raw.split())
    if not text or text.startswith("<"):
        return ""
    if len(text) > _DETAIL_MAX:
        text = text[: _DETAIL_MAX - 1].rstrip() + "…"
    return text if text[-1] in ".!?…" else text + "."


def _is_id_arg(name: str) -> bool:
    return name in _LOOKUP_BY_ARG or name.endswith(("_id", "_uuid")) or name == "ids"


def _not_found(tool: str, ids: Mapping[str, object]) -> str:
    quoted = ", ".join(f"{name}={_quote(value)}" for name, value in ids.items())
    lookups = sorted(
        {
            f"{name} with {_LOOKUP_BY_ARG.get(name) or _LOOKUP_BY_TOOL.get(tool, 'the matching list tool')}"
            for name in ids
        }
    )
    return (
        f"Paperless has nothing for {quoted} in {tool}. Check "
        f"{' and '.join(lookups)}, then call {tool} again."
    )


def _quote(value: object) -> str:
    """``repr`` of an id argument, shortened so a long ``ids`` list stays readable."""
    return reprlib.repr(value)


def _client_error(
    tool: str, status: int, detail: str, ids: Mapping[str, object]
) -> Outcome:
    """Classify a 4xx answer: the model changes the request, except for 401."""
    because = f": {detail}" if detail else "."
    if status == 401:
        return Outcome(
            f"Paperless did not accept this server's credentials, so {tool} "
            f"could not run. {_TELL_USER}",
            logging.ERROR,
        )
    if status == 403:
        message = (
            f"The Paperless account this server uses may not do what {tool} "
            "asked for this object. Tell the user; retrying will not help."
        )
    elif status == 404 and ids:
        message = _not_found(tool, ids)
    elif status == 404:
        # No id argument to be wrong: the route itself is missing, so the
        # Paperless URL or the instance's version is the problem, not the call.
        return Outcome(
            f"Paperless has no endpoint for {tool} at the configured address. "
            + _TELL_USER,
            logging.ERROR,
        )
    elif status == 409:
        message = (
            f"{tool} conflicts with the current state in Paperless{because} "
            "Resending the same call fails again; read the object again and "
            "retry with its current values."
        )
    elif status == 400:
        message = (
            f"Paperless rejected the arguments to {tool}{because} "
            f"Correct that value and call {tool} again."
        )
    else:
        message = (
            f"Paperless refused {tool}{because} Change the arguments before "
            f"calling {tool} again."
        )
    return Outcome(message, logging.INFO)


def classify(
    exc: PaperlessAPIError, tool: str, ids: Mapping[str, object] | None = None
) -> Outcome:
    """Map a Paperless API failure to the outcome the model receives.

    Args:
        exc: The failure the Paperless client raised.
        tool: Name of the tool whose call failed, quoted in the message.
        ids: The call's id arguments by name, quoted in a not-found message.

    Returns:
        The message for the model and the level to log it at.
    """
    status = exc.status_code
    if status == 0 or status == 429 or status >= 500:
        return _transient(tool)
    if 400 <= status < 500:
        return _client_error(tool, status, _detail(exc.detail), ids or {})
    return Outcome(
        f"Paperless answered {tool} with an unexpected status. {_TELL_USER}",
        logging.ERROR,
    )


def _raise(outcome: Outcome, cause: Exception) -> NoReturn:
    raise ToolError(outcome.message, log_level=outcome.log_level) from cause


def raise_classified(
    exc: PaperlessAPIError, tool: str, ids: Mapping[str, object] | None = None
) -> NoReturn:
    """Log what an operator needs, then raise the model-facing ``ToolError``.

    Args:
        exc: The failure the Paperless client raised.
        tool: Name of the tool whose call failed.
        ids: The call's id arguments by name, quoted in a not-found message.

    Raises:
        ToolError: Always, at the level :func:`classify` picks.
    """
    outcome = classify(exc, tool, ids)
    _log_upstream(outcome, tool, exc.status_code, exc.detail)
    _raise(outcome, exc)


def paperless_errors(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Translate Paperless failures without registering or changing a tool.

    Args:
        func: Domain coroutine, wrapped inside ``tool_boundary``.

    Returns:
        A signature-preserving coroutine that raises MCP ToolError on failure.
    """
    name = func.__name__
    signature = inspect.signature(func)

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
    # tool's output schema.  The request-logging middleware logs the message
    # as ``tool_call_failed`` at the error's level; the lines below add the
    # operator detail the message leaves out, for the outcomes an operator
    # may have to act on.
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except PaperlessAPIError as exc:
            raise_classified(exc, name, _id_args(signature, args, kwargs))
        except httpx.HTTPStatusError as exc:
            api_exc = error_from_response(exc.response)
            outcome = classify(api_exc, name, _id_args(signature, args, kwargs))
            _log_upstream(outcome, name, api_exc.status_code, api_exc.detail)
            _raise(outcome, exc)
        except httpx.RequestError as exc:
            logger.warning("tool_network_error tool=%s error=%s", name, exc)
            _raise(_transient(name), exc)
        except PydanticValidationError as exc:
            # Tool arguments are validated by FastMCP before the body runs, so
            # a pydantic error in here is Paperless answering in a shape the
            # models do not accept: a server-side fault the model cannot fix.
            logger.error(
                "tool_validation_error tool=%s errors=%d",
                name,
                exc.error_count(),
                exc_info=exc,
            )
            _raise(
                Outcome(
                    f"Paperless answered {name} in a shape this server cannot "
                    "read. The request was fine; tell the user, since retrying "
                    "will not help.",
                    logging.ERROR,
                ),
                exc,
            )

    return wrapper


def _log_upstream(outcome: Outcome, tool: str, status: int, detail: str) -> None:
    """Log what an operator needs; model-actionable outcomes need no line here."""
    if outcome.log_level >= logging.ERROR:
        logger.error("tool_api_error tool=%s status=%s detail=%s", tool, status, detail)
    elif outcome.log_level >= logging.WARNING:
        logger.warning(
            "tool_api_error tool=%s status=%s detail=%s", tool, status, detail
        )


def _id_args(
    signature: inspect.Signature, args: tuple[object, ...], kwargs: dict[str, object]
) -> dict[str, object]:
    """The id-like arguments of one call, by name, for a not-found message."""
    bound = signature.bind_partial(*args, **kwargs).arguments
    return {k: v for k, v in bound.items() if _is_id_arg(k) and v is not None}


def check_object_bulk_parameters(
    tool: str, parameters: Mapping[str, object] | None
) -> None:
    """Refuse keys the object bulk-edit endpoint would ignore or misuse.

    Args:
        tool: The bulk tool being called, named in the message.
        parameters: The ``parameters`` argument the model passed.

    Raises:
        ToolError: At INFO, naming the unsupported keys and the accepted ones.
    """
    extra = sorted(set(parameters or {}) - set(OBJECT_BULK_PARAMETERS))
    if extra:
        raise ToolError(
            f"parameters passed to {tool} has unsupported keys: {', '.join(extra)}. "
            "It takes only owner, permissions and merge, for set_permissions; "
            f"call {tool} again with those.",
            log_level=logging.INFO,
        )
