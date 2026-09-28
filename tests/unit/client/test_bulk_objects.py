"""The object bulk-edit body: permission fields at the top level, nothing else."""

from __future__ import annotations

import json
import logging

import httpx
import pytest
import respx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from paperless_mcp.client import PaperlessClient
from paperless_mcp.client._bulk_objects import object_bulk_payload


def test_permission_fields_go_to_the_top_level() -> None:
    body = object_bulk_payload(
        "tags", [1, 2], "set_permissions", {"owner": 3, "merge": True}
    )
    assert body == {
        "owner": 3,
        "merge": True,
        "object_type": "tags",
        "objects": [1, 2],
        "operation": "set_permissions",
    }


@pytest.mark.parametrize(
    "parameters",
    [
        {"operation": "delete"},
        {"all": True},
        {"object_type": "correspondents"},
        {"set_permissions": {"view": {"users": [1]}}},
    ],
)
def test_other_keys_are_refused(parameters: dict[str, object]) -> None:
    """``all``/``filters`` widen the selection and fixed keys must not move."""
    with pytest.raises(ValueError, match="unsupported"):
        object_bulk_payload("tags", [1], "set_permissions", parameters)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("resource", "object_type"),
    [
        ("tags", "tags"),
        ("correspondents", "correspondents"),
        ("document_types", "document_types"),
    ],
)
async def test_every_object_client_sends_the_same_shape(
    resource: str, object_type: str
) -> None:
    client = PaperlessClient(base_url="http://paperless.test", api_token="t")
    async with respx.mock(base_url="http://paperless.test") as mock:
        route = mock.post("/api/bulk_edit_objects/").mock(
            return_value=httpx.Response(200, json={"result": "OK"})
        )
        await getattr(client, resource).bulk_edit(
            operation="set_permissions", ids=[4], parameters={"owner": 3}
        )
    body = json.loads(route.calls.last.request.content)
    assert body["owner"] == 3
    assert body["object_type"] == object_type
    assert "parameters" not in body
    await client.aclose()


@pytest.mark.asyncio
async def test_tool_refuses_unsupported_keys_before_calling_paperless() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from paperless_mcp.tools import tags as tags_mod
    from paperless_mcp.tools._context import ToolContext

    client = MagicMock()
    client.tags.bulk_edit = AsyncMock()
    mcp = FastMCP("test")
    tags_mod.register(
        mcp, ToolContext(client=client, default_page_size=25, public_url="")
    )
    with pytest.raises(ToolError, match="unsupported keys for delete: all") as excinfo:
        await mcp.call_tool(
            "bulk_edit_tags",
            {"operation": "delete", "ids": [1], "parameters": {"all": True}},
        )
    assert excinfo.value.log_level == logging.INFO
    client.tags.bulk_edit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("operation", "parameters", "fragment"),
    [
        ("delete", {"owner": 3}, "delete takes no parameters"),
        ("set_permissions", {"all": True}, "set_permissions takes only owner"),
    ],
)
async def test_tool_checks_parameters_against_the_operation(
    operation: str, parameters: dict[str, object], fragment: str
) -> None:
    """``delete`` takes nothing; ``set_permissions`` takes the three fields."""
    from unittest.mock import AsyncMock, MagicMock

    from paperless_mcp.tools import tags as tags_mod
    from paperless_mcp.tools._context import ToolContext

    client = MagicMock()
    client.tags.bulk_edit = AsyncMock()
    mcp = FastMCP("test")
    tags_mod.register(
        mcp, ToolContext(client=client, default_page_size=25, public_url="")
    )
    with pytest.raises(ToolError, match=fragment):
        await mcp.call_tool(
            "bulk_edit_tags",
            {"operation": operation, "ids": [1], "parameters": parameters},
        )
    client.tags.bulk_edit.assert_not_awaited()


@pytest.mark.asyncio
async def test_tool_lets_set_permissions_fields_through() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from paperless_mcp.models.common import BulkEditResult
    from paperless_mcp.tools import tags as tags_mod
    from paperless_mcp.tools._context import ToolContext

    client = MagicMock()
    client.tags.bulk_edit = AsyncMock(return_value=BulkEditResult(result="OK"))
    mcp = FastMCP("test")
    tags_mod.register(
        mcp, ToolContext(client=client, default_page_size=25, public_url="")
    )
    await mcp.call_tool(
        "bulk_edit_tags",
        {"operation": "set_permissions", "ids": [1], "parameters": {"owner": 3}},
    )
    client.tags.bulk_edit.assert_awaited_once()
