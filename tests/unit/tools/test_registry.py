"""Domain error translation remains independent of registration."""

import pytest


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_paperless_api_error() -> None:
    from fastmcp.exceptions import ToolError

    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import paperless_errors

    async def boom() -> object:
        raise NotFoundError(404, "No Tag matches the given query.")

    wrapped = paperless_errors(boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Paperless API error 404:")
    assert "No Tag matches" in str(excinfo.value)
    # ``raise ... from exc`` must preserve the cause so the original Paperless
    # error remains visible in tracebacks and ``__cause__`` walks.
    assert isinstance(excinfo.value.__cause__, NotFoundError)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_httpx_status_error() -> None:
    import httpx
    from fastmcp.exceptions import ToolError

    from paperless_mcp.tools._errors import paperless_errors

    async def boom() -> object:
        request = httpx.Request("DELETE", "http://paperless.test/api/x/")
        response = httpx.Response(404, json={"detail": "Not found."}, request=request)
        raise httpx.HTTPStatusError("404", request=request, response=response)

    wrapped = paperless_errors(boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Paperless API error 404:")
    assert "Not found" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, httpx.HTTPStatusError)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_request_error() -> None:
    import httpx
    from fastmcp.exceptions import ToolError

    from paperless_mcp.tools._errors import paperless_errors

    async def boom() -> object:
        raise httpx.ConnectError("name resolution failed")

    wrapped = paperless_errors(boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert "Network error connecting to Paperless" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, httpx.ConnectError)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_pydantic_validation_error() -> None:
    from fastmcp.exceptions import ToolError
    from pydantic import BaseModel
    from pydantic import ValidationError as PydanticValidationError

    from paperless_mcp.tools._errors import paperless_errors

    class M(BaseModel):
        n: int

    async def boom() -> object:
        M.model_validate({"n": "not-an-int"})
        return None

    wrapped = paperless_errors(boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert str(excinfo.value).startswith("Response validation failed (1 error(s)):")
    assert isinstance(excinfo.value.__cause__, PydanticValidationError)


@pytest.mark.asyncio
async def test_core_jobs_preserves_metadata_and_domain_errors() -> None:
    """Path 1 composes metadata and errors for inline and promoted execution."""
    import asyncio
    from typing import Any

    from fastmcp import FastMCP
    from fastmcp.exceptions import ToolError
    from fastmcp_pvl_core import (
        JobsConfig,
        ServerConfig,
        build_jobs,
        register_job_tools,
        register_long_running_tool,
    )

    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import paperless_errors
    from paperless_mcp.tools._metadata import tool_metadata

    mcp = FastMCP("registration")
    jobs = build_jobs(
        ServerConfig(kv_store_url="memory://"), JobsConfig(soft_deadline_s=0.01)
    )
    finish = asyncio.Event()

    @register_long_running_tool(mcp, jobs, **tool_metadata("get_task"))
    @paperless_errors
    async def get_task(wait: bool = False, fail: bool = False) -> dict[str, Any]:
        """Exercise the actual core registrar with Paperless behavior."""
        if wait:
            await finish.wait()
        if fail:
            raise NotFoundError(404, "Task not found")
        return {"ok": True}

    register_job_tools(mcp, jobs)
    tool = await mcp.get_tool("get_task")
    assert tool is not None
    metadata = tool_metadata("get_task")
    assert tool.annotations == metadata["annotations"]
    assert tool.icons == metadata["icons"]
    assert tool.task_config.mode == "optional"
    assert set(tool.parameters["properties"]) == {"wait", "fail"}
    assert (await mcp.call_tool("get_task", {})).structured_content == {"ok": True}
    with pytest.raises(ToolError, match="Paperless API error 404: Task not found"):
        await mcp.call_tool("get_task", {"fail": True})

    for fail in (False, True):
        finish.clear()
        try:
            result = await mcp.call_tool("get_task", {"wait": True, "fail": fail})
            handle = result.structured_content
            assert handle is not None and handle["status"] == "working"
        finally:
            finish.set()
        async with asyncio.timeout(2):
            while True:
                result = await mcp.call_tool(
                    "get_job_result", {"job_id": handle["job_id"]}
                )
                polled = result.structured_content
                assert polled is not None
                if polled["status"] != "working":
                    break
                await asyncio.sleep(0.01)
        assert polled["status"] == ("failed" if fail else "completed")
        if fail:
            assert polled["error"] == "Paperless API error 404: Task not found"
        else:
            assert polled["result"] == {"ok": True}
