"""Tests for the secret-masking log filter."""

from __future__ import annotations

import logging

from paperless_mcp.client._http import _SecretMaskFilter


def test_masks_token_header() -> None:
    record = logging.LogRecord(
        "x",
        logging.DEBUG,
        "_",
        0,
        "headers={'Authorization': 'Token abcdef1234567890'}",
        None,
        None,
    )
    _SecretMaskFilter().filter(record)
    assert "abcdef1234567890" not in record.getMessage()
    assert "Token ***" in record.getMessage()


def test_masks_bearer_header() -> None:
    record = logging.LogRecord(
        "x",
        logging.DEBUG,
        "_",
        0,
        "Authorization: Bearer eyJhbGciOi...",
        None,
        None,
    )
    _SecretMaskFilter().filter(record)
    assert "eyJhbGciOi..." not in record.getMessage()
    assert "Bearer ***" in record.getMessage()


def test_passes_unrelated_messages_through() -> None:
    record = logging.LogRecord(
        "x",
        logging.DEBUG,
        "_",
        0,
        "plain debug message",
        None,
        None,
    )
    _SecretMaskFilter().filter(record)
    assert record.getMessage() == "plain debug message"
