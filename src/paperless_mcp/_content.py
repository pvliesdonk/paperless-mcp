"""Shared bounds for OCR text returned through MCP."""

from __future__ import annotations

#: Default ceiling for an inline OCR preview. The full text remains available
#: through offset paging and, on configured HTTP deployments, transfer links.
CONTENT_CHAR_CAP = 20_000


def _content_marker(*, offset: int, end: int, total: int) -> str:
    """Build the header that precedes a partial OCR section."""
    if offset >= total:
        return f"[offset {offset:,} is past the end of this document ({total:,} chars)]\n\n"
    if end >= total:
        return f"[chars {offset:,}-{total:,} of {total:,} - final section]\n\n"
    return (
        f"[chars {offset:,}-{end:,} of {total:,} - truncated; call "
        f"get_document_content again with offset={end} to continue, or use "
        "create_download_link with variant content if available]\n\n"
    )


def slice_content(
    text: str, *, max_chars: int = CONTENT_CHAR_CAP, offset: int = 0
) -> str:
    """Return OCR text from *offset*, bounded by *max_chars*.

    Args:
        text: Full OCR text.
        max_chars: Maximum characters to return.
        offset: Character position at which to begin.

    Returns:
        The requested section, with a marker when it is not the whole text.
    """
    total = len(text)
    end = min(total, offset + max_chars)
    if offset == 0 and end >= total:
        return text
    return _content_marker(offset=offset, end=end, total=total) + text[offset:end]
