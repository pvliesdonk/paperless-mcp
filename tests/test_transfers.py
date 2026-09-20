"""Document transfer contracts exercised through MCP minting and HTTP redemption."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import yaml
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp_pvl_core import ServerConfig, TransferConfig, TransferSinkError
from pydantic import ValidationError

from paperless_mcp._transfer_models import (
    DownloadHandle,
    UploadHandle,
    UploadMetadata,
    render_markdown,
)
from paperless_mcp.client._errors import PaperlessAPIError
from paperless_mcp.config import ProjectConfig
from paperless_mcp.models.common import UploadTaskAcknowledgement
from paperless_mcp.models.document import Document
from paperless_mcp.server import make_server
from paperless_mcp.tools._context import ToolContext
from paperless_mcp.transfers import PaperlessTransferSink, register_transfers

DOWNLOAD = "create_download_link"
UPLOAD = "create_upload_link"


@pytest.fixture
def document(load_fixture: Callable[[str], Any]) -> Document:
    doc = Document.model_validate(load_fixture("document_full.json"))
    return doc.model_copy(
        update={
            "title": 'A title: "quoted"\n---\ntags: [999]\u0085Café',
            "content": "# Notes\n\nCafé\n" + "Long OCR text. " * 5000,
            "original_file_name": "original.pdf",
            "archived_file_name": "archive.pdf",
        }
    )


@pytest.fixture
def ctx(document: Document) -> ToolContext:
    client = MagicMock()
    client.documents.get = AsyncMock(return_value=document)
    client.documents.download = AsyncMock(return_value=(b"pdf-data", "application/pdf"))
    client.documents.get_preview = AsyncMock(
        return_value=(b"preview-data", "application/pdf")
    )
    client.documents.upload = AsyncMock(
        return_value=UploadTaskAcknowledgement(task_id="task-123")
    )
    return ToolContext(client=client, default_page_size=25, public_url="")


@pytest.fixture
def config(tmp_path: Path) -> ProjectConfig:
    return ProjectConfig(
        server=ServerConfig(
            base_url="http://transfer.test",
            kv_store_url=f"file://{tmp_path / 'kv'}",
        ),
        transfer=TransferConfig(max_upload_bytes=200_000),
    )


@pytest.fixture
def mcp(ctx: ToolContext, config: ProjectConfig) -> FastMCP:
    server = FastMCP("transfers")
    register_transfers(server, ctx, config)
    return server


async def _mint(mcp: FastMCP, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    arguments = dict(arguments)
    ttl = {"ttl_s": arguments.pop("ttl_s")} if "ttl_s" in arguments else {}
    async with Client(mcp) as client:
        result = await client.call_tool(name, {"ref": json.dumps(arguments), **ttl})
    assert result.structured_content is not None
    assert set(result.structured_content) == {"url", "expires_in_s"}
    return dict(result.structured_content)


@pytest.mark.parametrize("variant", ["original", "archive", "preview", "content"])
async def test_download_variants(
    mcp: FastMCP, ctx: ToolContext, document: Document, variant: str
) -> None:
    link = await _mint(mcp, DOWNLOAD, {"document_id": document.id, "variant": variant})
    ctx.client.documents.download.assert_not_awaited()  # type: ignore[attr-defined]
    transport = httpx.ASGITransport(app=mcp.http_app())
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.get(link["url"])
    assert response.status_code == 200
    assert "attachment;" in response.headers["content-disposition"]
    if variant == "content":
        assert response.content == render_markdown(document)
        assert response.headers["content-type"].startswith("text/markdown")
        assert "document-" in response.headers["content-disposition"]
    elif variant == "preview":
        assert response.content == b"preview-data"
        ctx.client.documents.get_preview.assert_awaited_once_with(document.id)  # type: ignore[attr-defined]
    else:
        assert response.content == b"pdf-data"
        ctx.client.documents.download.assert_awaited_once_with(  # type: ignore[attr-defined]
            document.id, original=variant == "original"
        )


async def test_markdown_round_trip(
    mcp: FastMCP, ctx: ToolContext, document: Document
) -> None:
    download = await _mint(
        mcp, DOWNLOAD, {"document_id": document.id, "variant": "content"}
    )
    upload = await _mint(
        mcp,
        UPLOAD,
        {"filename": "notes.md", "metadata": {"title": "New notes", "tags": [2]}},
    )
    transport = httpx.ASGITransport(app=mcp.http_app())
    async with httpx.AsyncClient(transport=transport) as client:
        content = (await client.get(download["url"])).content
        response = await client.put(upload["url"], content=content)
    assert response.json() == {"task_id": "task-123"}
    ctx.client.documents.upload.assert_awaited_once_with(  # type: ignore[attr-defined]
        filename="notes.md", content=content, title="New notes", tags=[2]
    )
    front_matter, body = content.decode().split("\n---\n\n", 1)
    parsed = yaml.safe_load(front_matter.removeprefix("---\n"))
    assert parsed["title"] == document.title
    assert parsed["tags"] == document.tags
    assert body == document.content


async def test_upload_replay(ctx: ToolContext, config: ProjectConfig) -> None:
    handle = UploadHandle(
        expires_at=time.time() + 1000, operation_id="one", filename="notes.md"
    ).model_dump_json()
    sink = PaperlessTransferSink(ctx, config)
    result = await sink.write(handle, b"notes")
    # A fresh sink shares persistent receipts, including across process restarts.
    restarted = PaperlessTransferSink(ctx, config)
    assert await restarted.write(handle, b"notes") == result
    with pytest.raises(TransferSinkError) as error:
        await restarted.write(handle, b"different notes")
    assert error.value.status_code == 409
    ctx.client.documents.upload.assert_awaited_once()  # type: ignore[attr-defined]


async def test_transfer_routes(mcp: FastMCP, ctx: ToolContext) -> None:
    link = await _mint(mcp, UPLOAD, {"filename": "file.pdf", "ttl_s": 999999})
    assert link["expires_in_s"] == 86400
    transport = httpx.ASGITransport(app=mcp.http_app())
    async with httpx.AsyncClient(transport=transport) as client:
        assert (await client.get(link["url"])).status_code == 404
        assert (await client.head(link["url"])).status_code == 405
        assert (
            await client.put(link["url"], content=b"x" * 200_001)
        ).status_code == 413
        first = await client.put(link["url"], content=b"valid")
        second = await client.post(link["url"], content=b"valid")
        assert first.status_code == second.status_code == 200
        assert first.json() == second.json() == {"task_id": "task-123"}
        assert (await client.put(link["url"], content=b"changed")).status_code == 409
    ctx.client.documents.upload.assert_awaited_once()  # type: ignore[attr-defined]


async def test_upload_unknown_outcome(ctx: ToolContext, config: ProjectConfig) -> None:
    ctx.client.documents.upload.side_effect = PaperlessAPIError(0, "connection lost")  # type: ignore[attr-defined]
    sink = PaperlessTransferSink(ctx, config)
    handle = UploadHandle(
        expires_at=time.time() + 1000, operation_id="uncertain", filename="file.pdf"
    ).model_dump_json()
    with pytest.raises(TransferSinkError) as error:
        await sink.write(handle, b"file")
    assert error.value.status_code == 502
    with pytest.raises(TransferSinkError) as error:
        await sink.write(handle, b"file")
    assert error.value.status_code == 409
    ctx.client.documents.upload.assert_awaited_once()  # type: ignore[attr-defined]


async def test_concurrent_upload_retries(
    ctx: ToolContext, config: ProjectConfig
) -> None:
    entered = asyncio.Event()
    finish = asyncio.Event()

    async def delayed(**_kwargs: Any) -> UploadTaskAcknowledgement:
        entered.set()
        await finish.wait()
        return UploadTaskAcknowledgement(task_id="delayed")

    ctx.client.documents.upload.side_effect = delayed  # type: ignore[attr-defined]
    sink = PaperlessTransferSink(ctx, config)
    handle = UploadHandle(
        expires_at=time.time() + 1000, operation_id="slow", filename="file.pdf"
    ).model_dump_json()
    first = asyncio.create_task(sink.write(handle, b"file"))
    await entered.wait()
    try:
        with pytest.raises(TransferSinkError) as error:
            await sink.write(handle, b"file")
        assert error.value.status_code == 409
    finally:
        finish.set()
        await first
    assert await sink.write(handle, b"file") == {"task_id": "delayed"}
    ctx.client.documents.upload.assert_awaited_once()  # type: ignore[attr-defined]


@pytest.mark.parametrize("status", [403, 404, 429, 500, 0])
async def test_download_error_releases_link(
    mcp: FastMCP, ctx: ToolContext, document: Document, status: int
) -> None:
    link = await _mint(mcp, DOWNLOAD, {"document_id": document.id})
    ctx.client.documents.get.side_effect = PaperlessAPIError(status, "private detail")  # type: ignore[attr-defined]
    transport = httpx.ASGITransport(app=mcp.http_app())
    async with httpx.AsyncClient(transport=transport) as client:
        response = await client.get(link["url"])
        assert response.status_code == (status if 400 <= status < 500 else 502)
        assert b"private detail" not in response.content
        ctx.client.documents.get.side_effect = None  # type: ignore[attr-defined]
        assert (await client.get(link["url"])).status_code == 200


async def test_missing_archive(
    ctx: ToolContext, config: ProjectConfig, document: Document
) -> None:
    ctx.client.documents.get.return_value = document.model_copy(  # type: ignore[attr-defined]
        update={"archived_file_name": None}
    )
    sink = PaperlessTransferSink(ctx, config)
    with pytest.raises(TransferSinkError) as error:
        await sink.read(
            DownloadHandle(document_id=document.id, variant="archive").model_dump_json()
        )
    assert error.value.status_code == 404
    ctx.client.documents.download.assert_not_awaited()  # type: ignore[attr-defined]


@pytest.mark.parametrize("use_allow", [True, False])
async def test_visibility_rejects_existing_links(
    ctx: ToolContext, config: ProjectConfig, document: Document, use_allow: bool
) -> None:
    server = (
        replace(config.server, tools_allow=("get_document",))
        if use_allow
        else replace(config.server, tools_deny=(DOWNLOAD, UPLOAD))
    )
    sink = PaperlessTransferSink(ctx, replace(config, server=server))
    with pytest.raises(TransferSinkError) as error:
        await sink.read(
            DownloadHandle(document_id=document.id, variant="content").model_dump_json()
        )
    assert error.value.status_code == 403
    with pytest.raises(TransferSinkError) as error:
        await sink.write(
            UploadHandle(
                expires_at=time.time() + 1000, operation_id="hidden", filename="file.md"
            ).model_dump_json(),
            b"file",
        )
    assert error.value.status_code == 403


@pytest.mark.parametrize(
    "filename", ["", "../file.md", "a/b.pdf", "a\\b.pdf", "bad\n.md", ".", ".."]
)
async def test_invalid_filename(mcp: FastMCP, filename: str) -> None:
    with pytest.raises(ToolError):
        await _mint(mcp, UPLOAD, {"filename": filename})


@pytest.mark.parametrize("ttl", [0, -1])
async def test_invalid_ttl(mcp: FastMCP, ttl: float) -> None:
    with pytest.raises((ToolError, ValueError)):
        await _mint(mcp, UPLOAD, {"filename": "notes.md", "ttl_s": ttl})


async def test_invalid_document_and_metadata(mcp: FastMCP, ctx: ToolContext) -> None:
    with pytest.raises(ToolError):
        await _mint(mcp, DOWNLOAD, {"document_id": 0})
    with pytest.raises(ToolError):
        await _mint(mcp, DOWNLOAD, {"document_id": 1, "variant": "untrusted-path"})
    with pytest.raises(ValidationError):
        UploadMetadata(tags=[-1])
    ctx.client.documents.get.side_effect = PaperlessAPIError(404, "not found")  # type: ignore[attr-defined]
    with pytest.raises(ToolError, match="404"):
        await _mint(mcp, DOWNLOAD, {"document_id": 1})


@pytest.mark.parametrize(
    "transport,transfer_base,enabled",
    [
        ("stdio", "http://test", False),
        ("http", None, False),
        ("http", "http://test", True),
        ("sse", "http://test", True),
    ],
)
def test_server_wiring(
    transport: str, transfer_base: str | None, enabled: bool
) -> None:
    config = ProjectConfig(
        server=ServerConfig(base_url=transfer_base, kv_store_url="memory://")
    )
    server = make_server(config=config, transport=transport)
    tools = asyncio.run(server._list_tools())
    names = {tool.name for tool in tools}
    assert ({DOWNLOAD, UPLOAD} <= names) == enabled
    for tool in tools:
        assert tool.annotations and tool.annotations.title
        if tool.name in {DOWNLOAD, UPLOAD}:
            assert tool.icons
    if enabled:
        assert DOWNLOAD in (server.instructions or "")
        assert UPLOAD in (server.instructions or "")


def test_transfer_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLESS_MCP_TRANSFER_MAX_UPLOAD_BYTES", "12345")
    monkeypatch.setenv("PAPERLESS_MCP_TRANSFER_TTL_DEFAULT_S", "120")
    assert ProjectConfig.from_env().transfer.max_upload_bytes == 12345
    assert ProjectConfig.from_env().transfer.ttl_default_s == 120


def test_empty_content_and_original_filename(
    ctx: ToolContext, config: ProjectConfig, document: Document
) -> None:
    doc = document.model_copy(update={"content": None, "original_file_name": None})
    assert render_markdown(doc).endswith(b"---\n\n")
    ctx.client.documents.get.return_value = doc  # type: ignore[attr-defined]
    sink = PaperlessTransferSink(ctx, config)
    result = asyncio.run(
        sink.read(
            DownloadHandle(document_id=doc.id, variant="original").model_dump_json()
        )
    )
    assert result.filename == f"document-{doc.id}"


async def test_expired_link(mcp: FastMCP) -> None:
    link = await _mint(mcp, UPLOAD, {"filename": "file.md", "ttl_s": 0.02})
    await asyncio.sleep(0.05)
    transport = httpx.ASGITransport(app=mcp.http_app())
    async with httpx.AsyncClient(transport=transport) as client:
        assert (await client.put(link["url"], content=b"file")).status_code == 404


async def test_core_transfer_surface(mcp: FastMCP) -> None:
    """Core owns generic tool shape; domain notes describe validated refs."""
    async with Client(mcp) as client:
        tools = {tool.name: tool for tool in await client.list_tools()}
        assert set(tools) == {DOWNLOAD, UPLOAD}
        for name, example in (
            (DOWNLOAD, '{"document_id":42,"variant":"content"}'),
            (UPLOAD, '{"filename":"notes.md","metadata":{"tags":[2]}}'),
        ):
            tool = tools[name]
            assert set(tool.input_schema["properties"]) == {"ref", "ttl_s"}
            assert tool.annotations and tool.annotations.title
            assert tool.icons
            assert "Paperless ref is a JSON string" in (tool.description or "")
            result = await client.call_tool(name, {"ref": example})
            assert result.structured_content


@pytest.mark.parametrize(
    "name,ref",
    [
        (DOWNLOAD, "42"),
        (DOWNLOAD, "not json"),
        (DOWNLOAD, '{"document_id":1,"extra":true}'),
        (UPLOAD, '{"filename":"notes.md","operation_id":"caller-chosen"}'),
        (UPLOAD, '{"filename":"notes.md","expires_at":99999999999}'),
        (UPLOAD, '{"filename":"notes.md","metadata":{"tags":[-1]}}'),
    ],
)
async def test_invalid_core_refs(mcp: FastMCP, name: str, ref: str) -> None:
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="Response validation failed"):
            await client.call_tool(name, {"ref": ref})
