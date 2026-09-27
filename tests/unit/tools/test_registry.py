"""Domain error translation remains independent of registration."""

import logging

import pytest


@pytest.mark.parametrize(
    ("status", "level", "fragment"),
    [
        (400, logging.INFO, "rejected the arguments to boom: name is required."),
        (401, logging.ERROR, "did not accept this server's credentials"),
        (403, logging.INFO, "may not do what boom asked"),
        (404, logging.ERROR, "no endpoint for boom"),
        (400, logging.INFO, "rejected the arguments to boom: name is required."),
        (409, logging.INFO, "read the object again"),
        (418, logging.INFO, "Paperless refused boom: name is required."),
        (429, logging.WARNING, "retry in a minute"),
        (502, logging.WARNING, "retry in a minute"),
        (0, logging.WARNING, "retry in a minute"),
        (302, logging.ERROR, "tell the user, since retrying will not help"),
    ],
)
def test_classify_names_the_actor_by_level(
    status: int, level: int, fragment: str
) -> None:
    """Who has to act decides the level: model INFO, self-healing WARNING, operator ERROR."""
    from paperless_mcp.client._errors import PaperlessAPIError
    from paperless_mcp.tools._errors import classify

    outcome = classify(PaperlessAPIError(status, "name is required"), "boom")
    assert outcome.log_level == level
    assert fragment in outcome.message


@pytest.mark.parametrize(
    ("tool", "ids", "fragments"),
    [
        (
            "get_document",
            {"document_id": 42},
            ["nothing for document_id=42 in get_document", "with search_documents"],
        ),
        (
            "delete_document_note",
            {"document_id": 5, "note_id": 9},
            ["document_id=5, note_id=9", "note_id with get_document_notes"],
        ),
        ("bulk_edit_tags", {"ids": [1, 2]}, ["ids=[1, 2]", "ids with list_tags"]),
    ],
)
def test_not_found_quotes_the_ids_and_names_the_lookup(
    tool: str, ids: dict[str, object], fragments: list[str]
) -> None:
    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import classify

    message = classify(NotFoundError(404, "Not found."), tool, ids).message
    for fragment in fragments:
        assert fragment in message


def test_long_id_lists_are_shortened_in_the_message() -> None:
    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import classify

    message = classify(
        NotFoundError(404, "Not found."),
        "bulk_edit_documents",
        {"ids": list(range(5000))},
    ).message
    assert "..." in message
    assert len(message) < 400


@pytest.mark.parametrize(
    ("detail", "expected"),
    [
        ("<html><body><h1>413</h1></body></html>", "Paperless refused boom. Change"),
        ("x" * 1000, "…"),
        ('{"name": ["This field is required."]}', 'required."]}. Correct'),
    ],
)
def test_detail_is_cleaned_for_the_model(detail: str, expected: str) -> None:
    from paperless_mcp.client._errors import PaperlessAPIError
    from paperless_mcp.tools._errors import classify

    status = 413 if detail.startswith("<") else 400
    message = classify(PaperlessAPIError(status, detail), "boom").message
    assert expected in message
    assert "<html>" not in message
    assert len(message) < 400


@pytest.mark.asyncio
async def test_wrapper_binds_positional_id_arguments() -> None:
    from fastmcp.exceptions import ToolError

    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import paperless_errors

    async def get_tag(tag_id: int) -> object:
        raise NotFoundError(404, "Not found.")

    with pytest.raises(ToolError, match="tag_id=7 in get_tag"):
        await paperless_errors(get_tag)(7)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_paperless_api_error() -> None:
    from fastmcp.exceptions import ToolError

    from paperless_mcp.client._errors import NotFoundError
    from paperless_mcp.tools._errors import paperless_errors

    async def boom(tag_id: int) -> object:
        raise NotFoundError(404, "No Tag matches the given query.")

    wrapped = paperless_errors(boom)
    with pytest.raises(ToolError) as excinfo:
        await wrapped(tag_id=3)
    assert "nothing for tag_id=3 in boom" in str(excinfo.value)
    assert excinfo.value.log_level == logging.INFO
    # ``raise ... from exc`` must preserve the cause so the original Paperless
    # error remains visible in tracebacks and ``__cause__`` walks.
    assert isinstance(excinfo.value.__cause__, NotFoundError)


@pytest.mark.asyncio
async def test_wrap_raises_tool_error_on_httpx_status_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    import httpx
    from fastmcp.exceptions import ToolError

    from paperless_mcp.tools._errors import paperless_errors

    async def boom() -> object:
        request = httpx.Request("DELETE", "http://paperless.test/api/x/")
        response = httpx.Response(503, json={"detail": "Down."}, request=request)
        raise httpx.HTTPStatusError("503", request=request, response=response)

    wrapped = paperless_errors(boom)
    with caplog.at_level(logging.WARNING), pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert "retry in a minute" in str(excinfo.value)
    assert excinfo.value.log_level == logging.WARNING
    assert isinstance(excinfo.value.__cause__, httpx.HTTPStatusError)
    assert [r.msg.split()[0] for r in caplog.records] == ["tool_api_error"]


@pytest.mark.asyncio
async def test_wrap_logs_operator_detail_on_auth_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    from fastmcp.exceptions import ToolError

    from paperless_mcp.client._errors import AuthError
    from paperless_mcp.tools._errors import paperless_errors

    async def boom() -> object:
        raise AuthError(401, "Invalid token.")

    wrapped = paperless_errors(boom)
    with caplog.at_level(logging.INFO), pytest.raises(ToolError) as excinfo:
        await wrapped()
    assert excinfo.value.log_level == logging.ERROR
    # The model is told to involve the user; the operator gets Paperless's
    # own detail in the log, never in the message.
    assert "Invalid token" not in str(excinfo.value)
    assert [r.args for r in caplog.records] == [("boom", 401, "Invalid token.")]


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
    assert "retry in a minute" in str(excinfo.value)
    assert excinfo.value.log_level == logging.WARNING
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
    assert "in a shape this server cannot read" in str(excinfo.value)
    assert excinfo.value.log_level == logging.ERROR
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
    with pytest.raises(ToolError, match="no endpoint for get_task"):
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
            assert "no endpoint for get_task" in polled["error"]
        else:
            assert polled["result"] == {"ok": True}
