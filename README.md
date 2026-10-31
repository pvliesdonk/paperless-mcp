<!-- DOMAIN-README-BADGES-START -->
<!-- An optional project logo or header line above the title; kept across copier update. -->
<!-- DOMAIN-README-BADGES-END -->

# Paperless MCP

<!-- mcp-name: io.github.pvliesdonk/paperless-mcp -->

[![CI](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=pvliesdonk_paperless-mcp&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=pvliesdonk_paperless-mcp) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=pvliesdonk_paperless-mcp&metric=coverage)](https://sonarcloud.io/summary/new_code?id=pvliesdonk_paperless-mcp) [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=pvliesdonk_paperless-mcp&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=pvliesdonk_paperless-mcp) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=pvliesdonk_paperless-mcp&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=pvliesdonk_paperless-mcp) [![PyPI](https://img.shields.io/pypi/v/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![Python](https://img.shields.io/pypi/pyversions/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![License](https://img.shields.io/github/license/pvliesdonk/paperless-mcp)](LICENSE) [![Docker](https://img.shields.io/github/v/release/pvliesdonk/paperless-mcp?label=ghcr.io&logo=docker)](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://pvliesdonk.github.io/paperless-mcp/) [![llms.txt](https://img.shields.io/badge/llms.txt-available-brightgreen)](https://pvliesdonk.github.io/paperless-mcp/latest/llms.txt) [![Template](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/pvliesdonk/paperless-mcp/main/.copier-answers.yml&query=%24._commit&label=template)](https://github.com/pvliesdonk/fastmcp-server-template)

Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.

**[Documentation](https://pvliesdonk.github.io/paperless-mcp/)** | **[Config wizard](https://pvliesdonk.github.io/paperless-mcp/latest/reference/configuration-generator/)** | **[PyPI](https://pypi.org/project/pvliesdonk-paperless-mcp/)** | **[Docker](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp)**

<!-- DOMAIN-README-PITCH-START -->
This server gives an MCP client (Claude Desktop, Claude Code, claude.ai or any other) the API of an existing [Paperless-NGX](https://docs.paperless-ngx.com/) instance: one tool per Paperless operation, with the instance's own permissions. It adds no document store and no workflow of its own; what a task does with the tools is up to the model.

- **Documents:** full-text and filtered search, metadata, notes, history, thumbnails, and the OCR text in bounded sections.
- **Organising:** create, change, delete and bulk-edit tags, correspondents, document types and custom fields, and bulk operations on documents.
- **Files:** upload documents for Paperless to consume and wait on the task; over HTTP, one-time [transfer links](docs/deploy/transfer-links.md) move whole files outside the model's context.
- **The instance:** statistics, saved views, storage paths, share links, background tasks and the installed and newest Paperless versions.

With the server connected, a client can handle requests such as:

- **"Find last quarter's invoices from ACME."** The model searches with a correspondent filter, then reads each match's text.
- **"Tag these three documents as 'reviewed' and move them to the Accounting correspondent."** One bulk edit.
- **"Upload this PDF and wait until OCR finishes."** An upload, then a wait on its consume task, so the answer comes once the document is indexed.
- **"What changed on document 4213 in the last week?"** The document's audit log.
<!-- DOMAIN-README-PITCH-END -->

## Does it fit?

What the server can reach, what it changes and who gets in is set out in the [security model](docs/security-model.md); the block below says who it serves and where it stops.

<!-- DOMAIN-README-FIT-START -->
- **For:** people who already keep their documents in Paperless-NGX and want an MCP client to search, read, file and organise them.
- **Reaches:** one Paperless-NGX instance over its REST API, with one API token; the [security model](docs/security-model.md) lists what that token lets the tools read and change.
- **Limits:** the tools can do only what the token's Paperless user may do. They don't administer Paperless (users, mail rules, workflows), and the text they read is Paperless's own OCR.
<!-- DOMAIN-README-FIT-END -->

## Quick start

Pick the client you use. Each line installs the released version; the [Get started](docs/get-started/index.md) tutorials carry on from there.

**Claude Desktop.** Download the `.mcpb` bundle from the [releases page](https://github.com/pvliesdonk/paperless-mcp/releases) and open it with Claude Desktop (or **Settings** › **Extensions** › **Advanced settings** › **Install Extension…**). Claude Desktop asks for the required settings itself. [Tutorial](docs/get-started/claude-desktop.md).

**Claude Code.** Two commands inside Claude Code; the second asks for a scope. [Tutorial](docs/get-started/claude-code.md).

```text
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install paperless-mcp@pvliesdonk
```

**A client that runs a command** (stdio). To register it in Claude Code, see the [Claude Code](docs/get-started/claude-code.md) tutorial.

```bash
uv tool install "pvliesdonk-paperless-mcp"
paperless-mcp serve
```

**A server for remote clients** (streamable HTTP). [A remote server](docs/get-started/http-client.md) connects the clients.

```bash
docker run --rm -p 8000:8000 --env-file .env ghcr.io/pvliesdonk/paperless-mcp:latest
```

A `compose.yml` ships at the repository root and runs as-is: copy `.env.example` to `.env`, then `docker compose up -d`. [Deploy](docs/deploy/index.md) covers authentication, OIDC, a reverse proxy and system packages (`.deb`/`.rpm` on the releases page). The server answers `/health` and `/health/ready` outside the MCP mount, and its `get_server_info` tool reports the running version.

<!-- DOMAIN-README-EXTRAS-START -->
- `uv tool install "pvliesdonk-paperless-mcp[debug]"` adds `debugpy`, for attaching a debugger to a running server.
<!-- DOMAIN-README-EXTRAS-END -->

## Configuration

Everything is configured through environment variables with the `PAPERLESS_MCP_` prefix. The ones most installs set:

<!-- GENERATED-ENV-TABLE-DOMAIN-START — generated by scripts/gen_config_surface.py; do not edit -->
| Variable | Default | Required | Description |
|---|---|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | (none) | **Yes** | Base URL of the Paperless-NGX REST API, without a trailing slash. |
| `PAPERLESS_MCP_API_TOKEN` | (none) | **Yes** | Paperless service-account token used for outbound API requests. |
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | (none) | No | Public Paperless UI URL for user-visible links; defaults to PAPERLESS_URL. |
<!-- GENERATED-ENV-TABLE-DOMAIN-END -->

Every variable the server reads, the shared ones included, is in the [configuration reference](docs/reference/configuration.md); `.env.example` lists the same surface in copy-paste form, and the [config wizard](https://pvliesdonk.github.io/paperless-mcp/latest/reference/configuration-generator/) writes one for your deployment.

## Documentation

- [Security model](docs/security-model.md): what the server can reach, what it changes and who gets in.
- [Get started](docs/get-started/index.md): a first success with your client.
- [Deploy](docs/deploy/index.md): Docker, authentication, OIDC, reverse proxy.
- [Use](docs/use/index.md): the features, for real tasks.
- [Reference](docs/reference/configuration.md): configuration, [tools](docs/reference/tools/index.md), resources, prompts, command line.
- [Upgrade](docs/upgrade/index.md): release channels, and what an upgrade changes for your clients and your data.
- [Contribute](docs/contribute/index.md): local development, secrets, where a fix belongs; `CONTRIBUTING.md` and `SECURITY.md` at the root.

## Design decisions

<!-- DOMAIN-README-DESIGN-START -->
- **Read-only deployments use tool visibility, not a domain switch.** Set `PAPERLESS_MCP_TOOLS_DENY` (or `PAPERLESS_MCP_TOOLS_ALLOW`) to hide the mutating tools, including `create_upload_link` when transfers are enabled. The template applies visibility last in `make_server`, so hidden tools leave `tools/list` and are rejected on `tools/call`. Clients cannot invoke a write that will be refused, and the rule lives in one place for every server built on this template.
- **HTTP layer retries idempotent reads only.** `PAPERLESS_MCP_HTTP_RETRIES` applies to GETs on 5xx/network errors; writes never retry automatically, to avoid double-applying bulk edits or uploads.
- **Tool icons come from `Lucide`.** Every tool carries a `Lucide` icon hint so MCP clients that render icons (Claude Desktop) get a coherent visual surface. See `src/paperless_mcp/tools/_icons.py`.
- **Paperless API compatibility:** requests prefer payload version 10, with automatic version 9 fallback for Paperless 2.x after an explicit version rejection. Tasks include structured results and timing data while retaining the legacy fields. Saved-view visibility flags can now be `null`; Python consumers must handle that value. See [task tools](docs/reference/tools/tasks.md).
- **Models accept unknown upstream fields.** `Pydantic` models use lenient validation for list-endpoint responses so newer Paperless-NGX versions do not break the client (the `Document.some_future_paperless_field` test pins this behaviour).
- **No prompts ship in v1.** `prompts.py` is intentionally empty; prompts land as concrete user-workflow patterns emerge in practice.
<!-- DOMAIN-README-DESIGN-END -->

## Links

- [Documentation](https://pvliesdonk.github.io/paperless-mcp/) and its [llms.txt](https://pvliesdonk.github.io/paperless-mcp/latest/llms.txt)
- [FastMCP](https://gofastmcp.com) and [fastmcp-pvl-core](https://pypi.org/project/fastmcp-pvl-core/), which this server is built on
- [fastmcp-server-template](https://github.com/pvliesdonk/fastmcp-server-template), which generated this repository
