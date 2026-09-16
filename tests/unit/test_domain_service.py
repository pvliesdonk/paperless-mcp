"""The domain Service adopts the staged tool context and closes its client."""

from __future__ import annotations

import pytest

from paperless_mcp import domain


@pytest.mark.asyncio
async def test_service_adopts_the_staged_context_and_closes_its_client() -> None:
    """`start` takes the staged context; `stop` closes the client it held."""
    context = domain.build_tool_context()
    assert domain.pending_tool_context() is context

    service = domain.Service()
    assert await service.ping() == "not ready"
    assert await service.status() == {"ready": False}

    await service.start()
    assert domain.pending_tool_context() is None, "start should clear the slot"
    assert await service.ping() == "pong"
    assert await service.status() == {"ready": True}

    await service.stop()
    # `PaperlessHTTP` exposes no public "is this closed" accessor, so the
    # underlying httpx client is the only place the answer lives.
    assert context.client.http._client.is_closed
    assert await service.ping() == "not ready"


@pytest.mark.asyncio
async def test_stop_is_safe_when_nothing_was_staged() -> None:
    """A service whose lifespan starts with an empty slot still stops cleanly."""
    domain.build_tool_context()
    adopter = domain.Service()
    await adopter.start()

    orphan = domain.Service()
    await orphan.start()
    await orphan.stop()

    await adopter.stop()
