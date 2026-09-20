"""Payload-version differences at the Paperless HTTP boundary.

See docs/design/reference/paperless-api-versioning.md.
"""

from __future__ import annotations

from typing import Any

import httpx


def is_version_rejection(response: httpx.Response) -> bool:
    """Recognize DRF's rejection before a versioned view executes.

    Args:
        response: Upstream response to a version 10 request.

    Returns:
        Whether the response explicitly rejects the Accept-header version.
    """
    if response.status_code != 406:
        return False
    try:
        body = response.json()
    except ValueError:
        return False
    return isinstance(body, dict) and body.get("detail") == (
        'Invalid version in "Accept" header.'
    )


def request_params(
    path: str, params: dict[str, Any] | None, version: int
) -> dict[str, Any] | None:
    """Translate task filters only when the instance requires payload v9.

    Args:
        path: Requested API path.
        params: Parameters expressed in the version 10 vocabulary.
        version: Payload version selected for this request.

    Returns:
        Parameters for the selected version, without mutating the caller's dict.
    """
    if version != 9 or path != "/api/tasks/" or params is None:
        return params
    adapted = dict(params)
    adapted.pop("page", None)
    adapted.pop("page_size", None)
    if "status" in adapted:
        adapted["status"] = str(adapted["status"]).upper()
    if "task_type" in adapted:
        kind = adapted.pop("task_type")
        adapted["task_name"] = {
            "sanity_check": "check_sanity",
            "llm_index": "llmindex_update",
        }.get(kind, kind)
    return adapted


class PayloadVersion:
    """Select payload v10, remembering an explicit v9 fallback per session."""

    def __init__(self) -> None:
        self._version = 10

    async def request(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        options: dict[str, Any],
    ) -> httpx.Response:
        """Send a request, retrying only a pre-view version rejection.

        Args:
            client: Authenticated HTTP session.
            method: HTTP method, including writes rejected before execution.
            path: API path.
            options: HTTP payload and canonical query parameters.

        Returns:
            The upstream response; normal retries and errors belong to the
            HTTP client. A second rejection is returned without another retry.
        """
        while True:
            version = self._version
            response = await client.request(
                method,
                path,
                **{
                    **options,
                    "params": request_params(path, options.get("params"), version),
                },
                headers={"Accept": f"application/json; version={version}"},
            )
            if version == 10 and is_version_rejection(response):
                self._version = 9
                continue
            return response
