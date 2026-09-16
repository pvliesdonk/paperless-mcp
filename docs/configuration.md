# Configuration

Paperless MCP is configured via environment variables with the
``PAPERLESS_MCP_`` prefix.

## Common variables

See `fastmcp-pvl-core`'s README for the full list of universal
variables (`PAPERLESS_MCP_TRANSPORT`, `PAPERLESS_MCP_HOST`,
`PAPERLESS_MCP_PORT`, `PAPERLESS_MCP_HTTP_PATH`,
`PAPERLESS_MCP_BASE_URL`, auth vars, etc.).

## Server identity

These two let an operator rename an instance or override its
instructions, with no configuration beyond the variable itself:

- `PAPERLESS_MCP_SERVER_NAME`: the server name reported to clients and
  by `get_server_info`. Defaults to `paperless-mcp`.
- `PAPERLESS_MCP_INSTRUCTIONS`: replaces the default MCP instructions
  text. Unset, the scaffold builds the default (which advertises this
  override).

## Tool visibility

Operators can trim which tools this instance exposes. Each variable takes a
comma-separated list of explicit tool names:

- `PAPERLESS_MCP_TOOLS_ALLOW`: expose *only* the listed tools.
- `PAPERLESS_MCP_TOOLS_DENY`: hide the listed tools.

Hidden tools disappear from `tools/list` and are rejected on `tools/call`;
resources and prompts are unaffected. Setting both variables, or setting one
to a value with no names in it, is a startup error. A name matching no
registered tool is ignored, but an allowlist that matches nothing logs a
startup `WARNING` since the instance then exposes zero tools. See
`fastmcp-pvl-core`'s README for the full semantics.

## Background tasks

Every Paperless MCP instance wires a background-task backend at startup, so
a tool registered with `task=True` works with no extra setup. One variable
picks the backend:

- `PAPERLESS_MCP_TASKS_URL`: `memory://` runs tasks in-process and loses
  them on restart; `redis://...` is durable and shared across processes.

Unset, a `redis://` `PAPERLESS_MCP_KV_STORE_URL` is reused for tasks as
well, so a single URL configures every stateful subsystem. With neither set,
the backend falls back to `memory://`, which the server logs at startup when
running over HTTP. The queue name comes from the `PAPERLESS_MCP` prefix, so
two servers sharing one Redis do not share a queue.

Worker tuning stays on the native `FASTMCP_DOCKET_*` variables
(`FASTMCP_DOCKET_CONCURRENCY` and friends, listed in `.env.example`). Set the
backend through `PAPERLESS_MCP_TASKS_URL` rather than
`FASTMCP_DOCKET_URL`: the former wins when both are set, and the server warns
about the disagreement.

<!-- DOMAIN-CONFIG-VARS-START -->
`PAPERLESS_MCP_PAPERLESS_URL` and `PAPERLESS_MCP_API_TOKEN` are the two
variables the server cannot start without. `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL`
lets you name a different base URL for user-visible links than the internal API
URL the server calls; unset, it defaults to `PAPERLESS_MCP_PAPERLESS_URL`, and
trailing slashes are stripped from both.

A minimal `.env`:

```bash
PAPERLESS_MCP_PAPERLESS_URL=http://paperless.local:8000
PAPERLESS_MCP_API_TOKEN=abc123yourtokenhere
PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS=60
PAPERLESS_MCP_DEFAULT_PAGE_SIZE=50
```
<!-- DOMAIN-CONFIG-VARS-END -->
