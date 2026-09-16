"""The domain context is shared per server, and the Service closes its client."""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from paperless_mcp import domain
from paperless_mcp.config import ProjectConfig
from paperless_mcp.resources import register_resources
from paperless_mcp.tools import register_tools


@pytest.mark.asyncio
async def test_service_adopts_the_staged_context_and_closes_its_client() -> None:
    """`start` takes the staged context; `stop` closes the client it held."""
    mcp = FastMCP("test")
    context = domain.tool_context_for(mcp)
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


def test_tool_context_is_shared_per_server_whichever_registrar_runs_first() -> None:
    """Registration order is decided in template-owned `server.py`, so both
    registrars must resolve the same context, and a second server must not
    adopt the first one's client."""
    first = FastMCP("first")
    register_resources(first)
    resources_ctx = domain.pending_tool_context()
    register_tools(first)
    assert domain.pending_tool_context() is resources_ctx, (
        "register_tools re-staged a second context over the resources' one"
    )

    second = FastMCP("second")
    register_tools(second)
    assert domain.pending_tool_context() is not resources_ctx, (
        "a second server adopted the first server's client"
    )
    assert resources_ctx is not None
    assert resources_ctx.client.http._client.is_closed, (
        "staging over an unadopted context must close the client it held"
    )


@pytest.mark.asyncio
async def test_stop_is_safe_when_nothing_was_staged() -> None:
    """A service whose lifespan starts with an empty slot still stops cleanly."""
    domain.tool_context_for(FastMCP("test"))
    adopter = domain.Service()
    await adopter.start()

    orphan = domain.Service()
    await orphan.start()
    await orphan.stop()

    await adopter.stop()


@pytest.mark.asyncio
async def test_tool_context_for_builds_from_an_explicit_config() -> None:
    """A config handed in wins over the environment the autouse fixture presets."""
    mcp = FastMCP("explicit-config")
    config = ProjectConfig(
        paperless_url="http://explicit.test",
        # Test literal fed to a mocked transport, never a credential.
        api_token="t",
        default_page_size=7,
    )
    context = domain.tool_context_for(mcp, config)
    try:
        assert context.default_page_size == 7
        assert context.public_url == "http://explicit.test"
        assert domain.tool_context_for(mcp) is context, (
            "a second ask must return the staged context, not rebuild from env"
        )
    finally:
        service = domain.Service()
        await service.start()
        await service.stop()
