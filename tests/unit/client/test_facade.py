from __future__ import annotations

import pytest

from paperless_mcp.client import PaperlessClient


@pytest.mark.asyncio
async def test_facade_exposes_sub_clients() -> None:
    client = PaperlessClient(
        base_url="http://paperless.test", api_token="t", max_retries=0
    )
    try:
        assert client.documents is not None
        assert client.tags is not None
        assert client.correspondents is not None
        assert client.document_types is not None
        assert client.custom_fields is not None
        assert client.storage_paths is not None
        assert client.saved_views is not None
        assert client.share_links is not None
        assert client.tasks is not None
        assert client.system is not None
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_facade_is_async_context_manager() -> None:
    async with PaperlessClient(
        base_url="http://paperless.test", api_token="t", max_retries=0
    ) as client:
        assert client.documents is not None
