# Tool registration

Core's higher-level registrars are the default (#158). Path 2 requires a
concrete user requirement that Path 1 cannot meet, evidence of the limitation,
and a reason a shared upstream improvement is unsuitable. Local signatures
and wrappers are implementation choices, not requirements.

Ordinary domain tools use `@mcp.tool(**tool_metadata(name))` above
`@paperless_errors`. The metadata helper only returns the tool's name, icons
and annotations; it cannot register a tool. Icons use core's `make_icon`.
The error decorator only translates Paperless, HTTP and response-validation
failures into `ToolError`, preserving the callable's signature. It registers
nothing. Existing metadata registries remain domain data.

A long-running domain coroutine uses the same composition:

```python
@register_long_running_tool(mcp, jobs, **tool_metadata("get_task"))
@paperless_errors
async def get_task(...) -> dict[str, Any]:
    ...
```

The error decorator is inside core's execution wrapper so both foreground
and promoted execution translate the same failures. Core owns optional native
task registration, deadline promotion and polling. This issue proves that
composition in an integration test; it does not enable Jobs on existing tools
or change their timeouts. Production Jobs adoption belongs to its feature.

Transfers use core's `register_transfer_routes` with a Paperless sink,
reference validator and appended descriptions. Core owns their names,
metadata and workflow instructions, so these tools have no entries in the
local metadata registries. See [document transfers](document-transfers.md).

The [external contract](reference/core-tool-registration.md) records the
metadata and Jobs behavior checked against core 7.2.0. The full registry test
checks titles and annotations for domain and core tools, and icons for domain
and transfer tools. Core 7.2.0 does not attach an icon to `get_server_info`.
