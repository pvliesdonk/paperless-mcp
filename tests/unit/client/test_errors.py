"""Tests for the typed error hierarchy."""

from __future__ import annotations

import httpx
import pytest

from paperless_mcp.client import _errors as err


def _response(status: int, body: object) -> httpx.Response:
    return httpx.Response(
        status_code=status,
        json=body,
        request=httpx.Request("GET", "http://paperless.test/api/documents/"),
    )


@pytest.mark.parametrize(
    ("status", "expected_cls"),
    [
        (400, err.ValidationError),
        (401, err.AuthError),
        (403, err.AuthError),
        (404, err.NotFoundError),
        (409, err.ConflictError),
        (429, err.RateLimitError),
        (500, err.UpstreamError),
        (502, err.UpstreamError),
        (503, err.UpstreamError),
    ],
)
def test_error_from_response_status_mapping(
    status: int, expected_cls: type[err.PaperlessAPIError]
) -> None:
    response = _response(status, {"detail": "oops"})
    raised = err.error_from_response(response)
    assert isinstance(raised, expected_cls)
    assert raised.status_code == status
    assert "oops" in str(raised)


def test_error_from_response_unknown_status() -> None:
    response = _response(418, {"detail": "teapot"})
    raised = err.error_from_response(response)
    assert isinstance(raised, err.PaperlessAPIError)
    assert raised.status_code == 418


def test_error_from_response_non_json_body() -> None:
    response = httpx.Response(
        status_code=500,
        content=b"<html>Server Error</html>",
        request=httpx.Request("GET", "http://x"),
    )
    raised = err.error_from_response(response)
    assert isinstance(raised, err.UpstreamError)
    assert "500" in str(raised)


def test_retryable_classification() -> None:
    assert err.UpstreamError(500, "x").is_retryable() is True
    assert err.RateLimitError(429, "x").is_retryable() is True
    assert err.NotFoundError(404, "x").is_retryable() is False
    assert err.ValidationError(400, "x").is_retryable() is False
    assert err.AuthError(401, "x").is_retryable() is False
