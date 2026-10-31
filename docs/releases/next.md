# Next release

<!-- notes-range-end: e0c9f5372cf8501f806618bd46f2bbed54314b65 -->

<!-- RELEASE-SUMMARY NEXT START -->
Compared with v3.0.0, a failed tool call now tells the model what to do next and is logged at a level that matches who has to act, so a mistaken call no longer logs at ERROR. Bulk permission edits on tags, correspondents and document types, and the `custom_field` filter on `list_documents`, now reach Paperless. Every tool parameter carries a description. The shipped `compose.yml` publishes on loopback only, the change that makes this a major release. The image moves to Debian trixie with tini as PID 1, and the runtime picks up fixes for published advisories in `authlib`, `pyjwt`, `joserfc`, `pydantic`, `fastmcp`, `dnspython` and `opentelemetry-api`. Read Upgrading first if you run the shipped `compose.yml` or send `redo_ocr`.
<!-- RELEASE-SUMMARY NEXT END -->

## Upgrading

- If you run the shipped `compose.yml` and reach the server from other
  machines, it now answers on `127.0.0.1:8000` only. Configure a bearer token
  or OIDC in `.env` first, then publish wider from `compose.override.yml`:

  ```yaml
  services:
    paperless-mcp:
      ports: !override
        - "8000:8000"
  ```

  A reverse proxy that reaches the container over a shared Docker network is
  unaffected ([Docker deployment](../deploy/docker.md), [#194](https://github.com/pvliesdonk/paperless-mcp/pull/194)).
- If you alert on ERROR-level tool logs, expect fewer: a mistaken call
  now logs at INFO and an upstream outage at WARNING (see the next section).
- If you build a derived image that calls `/usr/local/bin/python` or `pip`,
  switch to `uv` or `/app/.venv/bin/python`; the new base image has neither.

**Clients:** reconnect to pick up the new descriptions. A client that sends
`bulk_edit_documents` with `operation: "redo_ocr"` must send `reprocess`
instead. `operation` on `bulk_edit_tags`, `bulk_edit_correspondents` and
`bulk_edit_document_types` now accepts only `set_permissions` or `delete`, the
two values Paperless acts on. No parameter was added, removed or renamed.

**State:** none. The KV store, its default location and its format are
unchanged.

**Security posture:** the shipped `compose.yml` no longer listens on every
interface. The runtime closure picks up the advisory fixes listed under
[Dependency security fixes](#dependency-security-fixes). No route, auth
default or write tool was added.

## Failed tool calls say who has to act

In v3.0.0 every failed tool call came back to the model as
`Paperless API error <status>: <detail>` and was logged at ERROR. The
motivating report ([#188](https://github.com/pvliesdonk/paperless-mcp/issues/188)):
"Expected a tool call with a wrong document id to tell the model how to
recover and to log at INFO; got `Paperless API error 404: No Document matches
the given query.` with no next step, logged at ERROR."

Each outcome is now sorted by who has to act, and the message and log level
follow from that ([#195](https://github.com/pvliesdonk/paperless-mcp/pull/195)):

| Paperless answered | Logged at | The model is told |
|---|---|---|
| 400, 403 or another 4xx | INFO | what to change in the call |
| 404 on a call with id arguments | INFO | the ids it sent, and the tool that looks each one up |
| 409 | INFO | to read the object again and retry with its current values |
| 429, 5xx or a network failure | WARNING | to retry in a minute |
| 401, a 404 on a call without id arguments, an unexpected status, or a reply the server cannot read | ERROR | to tell the user |

The request log's `tool_call_failed` line now carries the error's own level
rather than always ERROR, and an exception that is not a tool error is logged
once as `tool_failed` with a traceback while the model gets a fixed retry
message ([fastmcp-pvl-core#374](https://github.com/pvliesdonk/fastmcp-pvl-core/pull/374)).
The `tool_http_status_error` event is gone; that path logs `tool_api_error`.

A few calls that used to misbehave now refuse up front, at INFO:

- `wait_for_task` reports a task still running at the deadline as an error
  that says what to call next, after one last read in case it finished.
- `upload_document` refuses invalid base64 instead of dropping the stray
  characters; line-wrapped base64 still decodes.
- `create_download_link` with `variant: "archive"` on a document without an
  archived PDF is refused when the link is made, and suggests the `original` variant.
  Before, the link was created and failed when used.

## Bulk edits and filters that reach Paperless

Two bulk operations and one filter sent requests Paperless did not act on
([#196](https://github.com/pvliesdonk/paperless-mcp/pull/196),
[#197](https://github.com/pvliesdonk/paperless-mcp/pull/197)):

- **`set_permissions` on tags, correspondents and document types.** The
  permissions travelled in a key Paperless ignores, and it answered `OK`
  ([#190](https://github.com/pvliesdonk/paperless-mcp/issues/190)). They are
  now sent where Paperless reads them. `operation` on `bulk_edit_tags`,
  `bulk_edit_correspondents` and `bulk_edit_document_types` accepts
  `set_permissions` or `delete` only, and parameters other than `owner`,
  `permissions` and `merge` are refused.
- **`redo_ocr` on `bulk_edit_documents`.** It "is not a method in Paperless
  3.x" ([#189](https://github.com/pvliesdonk/paperless-mcp/issues/189)). It
  is replaced by `reprocess`, and `edit_pdf` and `remove_password` are added.
- **`custom_field` on `list_documents`.** The filter had no effect
  ([#192](https://github.com/pvliesdonk/paperless-mcp/issues/192)); it now
  sends `custom_fields__id__in`, which Paperless declares. The parameter name
  is unchanged.

## A description on every parameter

"Of 52 tools, only `get_document_content` and the two transfer-link tools
describe any parameter" ([#191](https://github.com/pvliesdonk/paperless-mcp/issues/191)).
Every parameter now has a description, and each tool description states what
the call does and returns, leaving failure handling to the error text above
([#197](https://github.com/pvliesdonk/paperless-mcp/pull/197)). Two titles
were corrected to match what the tools always did: `delete_document` is "Move
Document to Trash" and `bulk_edit_tags` is titled "Bulk Edit Tags" now. The same
descriptions now publish as the [tools reference](../reference/tools/index.md).

## Startup refuses a missing URL or token in one line

`PAPERLESS_MCP_PAPERLESS_URL` and `PAPERLESS_MCP_API_TOKEN` are declared
required. When one is unset, `serve` exits with
`ERROR: configuration error: PAPERLESS_MCP_PAPERLESS_URL is required but not set`
instead of a traceback raised while the server was built
([#186](https://github.com/pvliesdonk/paperless-mcp/issues/186),
[#194](https://github.com/pvliesdonk/paperless-mcp/pull/194)). Out-of-range
timeout, retry and page-size values, and a malformed KV or event store URL,
stop the server the same way. `paperless-mcp -v serve` now keeps the
verbosity `-v` asks for ([#214](https://github.com/pvliesdonk/paperless-mcp/pull/214)).

## Container image

The image is built on `debian:trixie-slim` with a uv-managed CPython 3.14 in
place of `python:3.14-slim`, so the Python version is unchanged
([#214](https://github.com/pvliesdonk/paperless-mcp/pull/214),
[template v11.5 upgrade notes](https://github.com/pvliesdonk/fastmcp-server-template/blob/v11.5.1/upgrading/v11.5.md)).
tini now runs as PID 1 and reaps child processes; overriding `--entrypoint`
bypasses it. Health check, ports, volumes and the entrypoint script are
unchanged.

## Dependency security fixes

These packages ship in the Docker image and the PyPI install, and each new
version fixes the advisories listed, at the severity the advisory states:

| Package | v3.0.0 | Now | Advisories |
|---|---|---|---|
| `authlib` | 1.7.2 | 1.9.1 | [GHSA-6v38-4h7w-rj9h](https://github.com/advisories/GHSA-6v38-4h7w-rj9h) (critical), [GHSA-7vr2-2fgp-9w7p](https://github.com/advisories/GHSA-7vr2-2fgp-9w7p) (high), and five medium or low ([#211](https://github.com/pvliesdonk/paperless-mcp/pull/211)) |
| `pyjwt` | 2.13.0 | 2.15.0 | [GHSA-pxh4-856f-4h89](https://github.com/advisories/GHSA-pxh4-856f-4h89) and [GHSA-p4g4-x82p-q773](https://github.com/advisories/GHSA-p4g4-x82p-q773) (high), and two medium ([#205](https://github.com/pvliesdonk/paperless-mcp/pull/205)) |
| `joserfc` | 1.7.4 | 1.7.6 | [GHSA-jpxq-7h8p-2q76](https://github.com/advisories/GHSA-jpxq-7h8p-2q76) (high), [GHSA-9pg5-8c7x-5hfx](https://github.com/advisories/GHSA-9pg5-8c7x-5hfx) (medium) ([#210](https://github.com/pvliesdonk/paperless-mcp/pull/210)) |
| `pydantic` | 2.13.5 | 2.14.2 | [GHSA-qpmf-fgh3-ff25](https://github.com/pydantic/pydantic/security/advisories/GHSA-qpmf-fgh3-ff25), [GHSA-3r8g-cqwr-jr29](https://github.com/pydantic/pydantic/security/advisories/GHSA-3r8g-cqwr-jr29) (medium) ([#203](https://github.com/pvliesdonk/paperless-mcp/pull/203)) |
| `fastmcp` | 4.0.4 | 4.1.4 | [GHSA-7xgj-8392-5q4r](https://github.com/advisories/GHSA-7xgj-8392-5q4r), [GHSA-vqqp-x5qm-5qp4](https://github.com/advisories/GHSA-vqqp-x5qm-5qp4) (medium) ([#221](https://github.com/pvliesdonk/paperless-mcp/pull/221)) |
| `dnspython` | 2.8.0 | 2.9.1 | [GHSA-45c3-73f7-pv4m](https://github.com/advisories/GHSA-45c3-73f7-pv4m) (high) ([#221](https://github.com/pvliesdonk/paperless-mcp/pull/221)) |
| `opentelemetry-api` | 1.44.0 | 1.45.2 | [GHSA-xcq7-p3pf-p88h](https://github.com/advisories/GHSA-xcq7-p3pf-p88h) (medium) ([#221](https://github.com/pvliesdonk/paperless-mcp/pull/221)) |

A package in this list is part of what the server installs; whether a given
deployment reaches the affected code depends on its configuration, which
these notes don't assess. `fastmcp` 4.1.4 also requires `redis!=8.1.0`, so the
image carries `redis` 8.0.1.

## Documentation

The documentation site is reorganised into Get started, Deploy, Use,
Reference and Upgrade sections, and the tool and resource pages are generated
from the server itself ([#214](https://github.com/pvliesdonk/paperless-mcp/pull/214),
[#215](https://github.com/pvliesdonk/paperless-mcp/pull/215),
[#217](https://github.com/pvliesdonk/paperless-mcp/pull/217)). Every page
address from v3.0.0 redirects to its new place, so bookmarks keep working.
