---
type: Reference
title: Core tool registration composition
description: Metadata forwarding, icon construction and Jobs error boundaries.
subject_version: "fastmcp-pvl-core 7.2.0"
valid_for: "fastmcp-pvl-core 7.x"
generated:
  by: process:researching-references
  at: 2026-09-20
verified:
  - by: process:researching-references-refute
    at: 2026-09-20
stale_after: 2027-03-20
status: stable
sources:
  - id: jobs
    title: Core Jobs registrar
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_jobs/register.py
    accessed: 2026-09-20
  - id: manager
    title: Jobs execution and result handling
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_jobs/manager.py
    accessed: 2026-09-20
  - id: icons
    title: Core icon helpers
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_icons.py
    accessed: 2026-09-20
---

# Core tool registration composition

Checked against installed core 7.2.0 for #158. The consumer is Paperless's
metadata/error composition, not a replacement Jobs implementation.

- `register_long_running_tool(mcp, jobs, **tool_kwargs)` passes metadata
  through to `mcp.tool`. It accepts name, icons and annotations; `task` is
  reserved and rejected as a caller kwarg. Core sets
  `TaskConfig(mode="optional")`. [source: jobs]
  [pins: tests/unit/tools/test_registry.py::test_core_jobs_preserves_metadata_and_domain_errors]
- The registrar uses `functools.wraps` and passes the domain coroutine into
  `Jobs.run_with_deadline`. A domain error decorator inside this wrapper runs
  both before and after promotion. Inline exceptions propagate; promoted
  failures store the exception text for the generic poller. [source: jobs]
  [source: manager]
  [pins: tests/unit/tools/test_registry.py::test_core_jobs_preserves_metadata_and_domain_errors]
- `make_icon(path)` builds an MCP icon with an extension-derived MIME type
  and base64 data URI; SVG is supported. Local SVG encoders are unnecessary.
  [source: icons] [pins: tests/unit/tools/test_icons.py::test_every_icon_entry_decodes]

The integration test checks optional task registration but does not exercise
a native client/Docket execution. That execution machinery stays core's
responsibility. Transfer registration has a different metadata ownership
contract, recorded in [transfer links](core-transfer-links.md).
The project's chosen composition is in [tool registration](../tool-registration.md).
