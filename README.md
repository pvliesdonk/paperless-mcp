# Paperless MCP

<!-- mcp-name: io.github.pvliesdonk/paperless-mcp -->

[![CI](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/pvliesdonk/paperless-mcp/graph/badge.svg)](https://codecov.io/gh/pvliesdonk/paperless-mcp) [![PyPI](https://img.shields.io/pypi/v/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![Python](https://img.shields.io/pypi/pyversions/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![License](https://img.shields.io/github/license/pvliesdonk/paperless-mcp)](LICENSE) [![Docker](https://img.shields.io/github/v/release/pvliesdonk/paperless-mcp?label=ghcr.io&logo=docker)](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://pvliesdonk.github.io/paperless-mcp/) [![llms.txt](https://img.shields.io/badge/llms.txt-available-brightgreen)](https://pvliesdonk.github.io/paperless-mcp/llms.txt) [![Template](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/pvliesdonk/paperless-mcp/main/.copier-answers.yml&query=%24._commit&label=template)](https://github.com/pvliesdonk/fastmcp-server-template)

Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.

**[Documentation](https://pvliesdonk.github.io/paperless-mcp/)** | **[Config wizard](https://pvliesdonk.github.io/paperless-mcp/latest/configuration-generator/)** | **[PyPI](https://pypi.org/project/pvliesdonk-paperless-mcp/)** | **[Docker](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp)**

## Features

<!-- DOMAIN-START -->
- **Document search & retrieval:** full-text and filtered list queries against Paperless-NGX, plus access to extracted OCR text, metadata, and thumbnails.
- **Tag, correspondent, document-type, custom-field management:** full CRUD and bulk-edit for every classification dimension Paperless exposes.
- **Document lifecycle** supports uploads, field changes, notes, audit history, and AI-suggested tags/correspondents/types.
- **Operational introspection** covers saved views, storage paths, share links, background tasks (with `wait_for_task`), statistics, and remote Paperless-NGX version.
- **MCP tools:** 50 LLM-visible tools with `Lucide` icons and read-only gating; see `src/paperless_mcp/tools/`.
- **MCP resources:** 20 URIs exposing documents and domain collections; see `src/paperless_mcp/resources/`.
- **Read-only mode:** flip `PAPERLESS_MCP_READ_ONLY=true` to disable every mutating tool at startup.
<!-- DOMAIN-END -->

## What you can do with it

<!-- DOMAIN-START -->
With this server mounted in an MCP client (Claude, etc.), you can:

- **"Find last quarter's invoices from ACME."** Composes `search_documents` with a correspondent filter, then streams matches via `paperless://documents/{id}/content`.
- **"Tag these three documents as 'reviewed' and move them to the Accounting correspondent."** Uses `bulk_edit_documents` in a single call.
- **"Upload this PDF and wait until OCR finishes."** Composes `upload_document` + `wait_for_task` so the assistant only reports back once the document is indexed.
- **"What changed on document 4213 in the last week?"** Reads `paperless://documents/4213/history` and summarises the audit trail.
<!-- DOMAIN-END -->

<!-- ===== TEMPLATE-OWNED SECTIONS BELOW — DO NOT EDIT; CHANGES WILL BE OVERWRITTEN ON COPIER UPDATE ===== -->

## Installation

### From PyPI

```bash
pip install pvliesdonk-paperless-mcp
```

If you add optional extras via the `PROJECT-EXTRAS-START` / `PROJECT-EXTRAS-END` sentinels in `pyproject.toml`, document them below:

<!-- DOMAIN-START -->
- `pip install pvliesdonk-paperless-mcp[docs]`: installs `mkdocs-material` and `mkdocstrings[python]` for building the documentation site locally (`uv run mkdocs serve`).
<!-- DOMAIN-END -->

### From source

```bash
git clone https://github.com/pvliesdonk/paperless-mcp.git
cd paperless-mcp
uv sync --all-extras --all-groups
```

### Docker

```bash
docker pull ghcr.io/pvliesdonk/paperless-mcp:latest
```

A `compose.yml` ships at the repo root as a starting point. Copy `.env.example` to `.env`, edit, and `docker compose up -d`.

To attach a remote Python debugger (development only; the protocol is unauthenticated), see [Remote debugging](docs/deployment/docker.md#remote-debugging).

### Linux packages (.deb / .rpm)

Download `.deb` or `.rpm` packages from the [GitHub Releases](https://github.com/pvliesdonk/paperless-mcp/releases) page. Both install a hardened systemd unit; env configuration is sourced from `/etc/paperless-mcp/env` (copy from the shipped `/etc/paperless-mcp/env.example`).

### Claude Desktop (.mcpb bundle)

Download the `.mcpb` bundle from the [GitHub Releases](https://github.com/pvliesdonk/paperless-mcp/releases) page and double-click to install, or run:

```bash
mcpb install paperless-mcp-<version>.mcpb
```

Claude Desktop prompts for required env vars via a GUI wizard, with no manual JSON editing needed.

For manual Claude Desktop configuration and setup options, see [Claude Desktop deployment](docs/deployment/claude-desktop.md).

## Quick start

```bash
paperless-mcp serve                                # stdio transport
paperless-mcp serve --transport http --port 8000   # streamable HTTP
```

For library usage (embedding the domain logic without the MCP transport), import from the `paperless_mcp` package directly. See the project's domain modules under `src/paperless_mcp/` for entry points.

### Server info

The server registers a built-in `get_server_info` tool (via `fastmcp_pvl_core.register_server_info_tool`) so operators can confirm the deployed version with a single MCP call. The default response carries `server_name`, `server_version`, and `core_version`. Servers that talk to a remote upstream wire upstream version reporting inside the `DOMAIN-UPSTREAM-START` / `DOMAIN-UPSTREAM-END` sentinel in `src/paperless_mcp/server.py`; see [`CLAUDE.md`](CLAUDE.md#server-info-tool-get_server_info) for the wiring pattern.

## Configuration

All settings come from environment variables with the `PAPERLESS_MCP_` prefix.

### Required

| Variable | Description |
|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | Base URL of the Paperless-NGX REST API (no trailing slash). |
| `PAPERLESS_MCP_API_TOKEN` | Paperless service-account token. |

### Optional (with defaults)

| Variable | Default | Description |
|---|---|---|
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | *(same as `PAPERLESS_MCP_PAPERLESS_URL`)* | Public-facing Paperless UI URL used to construct user-visible links, including `web_url` and `share_url`. Defaults to the API URL when unset. |
| `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` | `30` | Per-request HTTP timeout (seconds). |
| `PAPERLESS_MCP_HTTP_RETRIES` | `2` | Retries (not counting the initial attempt) on 5xx/network errors. |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` | `25` | Default `page_size` for list tools. Clamped `[1, 100]`. |
| `PAPERLESS_MCP_READ_ONLY` | `false` | When `true`, disables every writable tool. |
| `PAPERLESS_MCP_INSTRUCTIONS` | *(built-in)* | Operator-supplied description appended to MCP instructions. |

See the [Transport & Auth](#transport--auth) section below for the inherited transport, auth, and logging variables.

## Transport & Auth

The following variables are inherited unchanged from [`fastmcp-server-template`](https://github.com/pvliesdonk/fastmcp-server-template):

| Variable | Description |
|---|---|
| `PAPERLESS_MCP_TRANSPORT` | Server transport: `stdio` (default), `http`, or `sse`. |
| `PAPERLESS_MCP_HOST` | Bind host for HTTP/SSE transport (default `127.0.0.1`). |
| `PAPERLESS_MCP_PORT` | Bind port for HTTP/SSE transport (default `8000`). |
| `PAPERLESS_MCP_HTTP_PATH` | URL path prefix for HTTP transport (default `/mcp`). |
| `PAPERLESS_MCP_BASE_URL` | Public base URL for OIDC and public HTTP server metadata. |
| `PAPERLESS_MCP_OIDC_*` | OIDC provider settings when OIDC auth is enabled. |
| `PAPERLESS_MCP_BEARER_TOKEN` | Static bearer token for simple token auth. |
| `PAPERLESS_MCP_LOG_LEVEL` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `PAPERLESS_MCP_LOG_FORMAT` | Log format: `rich` (default) or `json`. |

## Tools

### Documents

| Tool | Description |
|---|---|
| `list_documents` | List documents with optional filtering; OCR `content` stripped by default (`include_content=True` for full text). `notes[].note` and `custom_fields[].value` are always stripped on listings. Use single-document endpoints to fetch them. |
| `search_documents` | Full-text search across documents; OCR `content` stripped by default (`include_content=True` for full text). `notes[].note` and `custom_fields[].value` are always stripped on search hits. |
| `get_document` | Retrieve a document by ID; OCR `content` stripped by default (`include_content=True` for full text) |
| `get_document_content` | Get the extracted text content of a document |
| `get_document_thumbnail` | Get the thumbnail image of a document |
| `get_document_metadata` | Get metadata (original filename, checksums, etc.) |
| `get_document_notes` | List notes attached to a document |
| `get_document_history` | Get the audit history of a document |
| `get_document_suggestions` | Get AI-generated tag/correspondent/type suggestions |
| `update_document` | Update document fields (title, tags, correspondent, etc.); response OCR `content` stripped by default (`include_content=True` to retain) |
| `delete_document` | Delete a document |
| `upload_document` | Upload a new document for processing |
| `bulk_edit_documents` | Apply a bulk operation to multiple documents |
| `add_document_note` | Add a note to a document |
| `delete_document_note` | Delete a note from a document |

`get_document`, `list_documents`, `search_documents`, and `update_document` include a `web_url` field pointing to the document in the Paperless UI, such as `https://paperless.example.com/documents/42/`. Set `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` if the public URL differs from the API URL; otherwise the API URL is used.

Paginated tools return `next`/`previous` as bare `page=N` markers (never full URLs). Callers pass `page=N` explicitly when walking pages. `None` means no further page.

### Tags

| Tool | Description |
|---|---|
| `list_tags` | List all tags |
| `get_tag` | Get a tag by ID |
| `create_tag` | Create a new tag |
| `update_tag` | Update a tag |
| `delete_tag` | Delete a tag |
| `bulk_edit_tags` | Bulk edit tags |

### Correspondents

| Tool | Description |
|---|---|
| `list_correspondents` | List all correspondents |
| `get_correspondent` | Get a correspondent by ID |
| `create_correspondent` | Create a new correspondent |
| `update_correspondent` | Update a correspondent |
| `delete_correspondent` | Delete a correspondent |
| `bulk_edit_correspondents` | Bulk edit correspondents |

### Document Types

| Tool | Description |
|---|---|
| `list_document_types` | List all document types |
| `get_document_type` | Get a document type by ID |
| `create_document_type` | Create a new document type |
| `update_document_type` | Update a document type |
| `delete_document_type` | Delete a document type |
| `bulk_edit_document_types` | Bulk edit document types |

### Custom Fields

| Tool | Description |
|---|---|
| `list_custom_fields` | List all custom fields |
| `get_custom_field` | Get a custom field by ID |
| `create_custom_field` | Create a new custom field |
| `update_custom_field` | Update a custom field |
| `delete_custom_field` | Delete a custom field |

### Observability

| Tool | Description |
|---|---|
| `list_storage_paths` | List storage paths |
| `get_storage_path` | Get a storage path by ID |
| `list_saved_views` | List saved views |
| `get_saved_view` | Get a saved view by ID |
| `list_share_links` | List share links (includes `share_url`; uses `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` if set, otherwise `PAPERLESS_MCP_PAPERLESS_URL`) |
| `get_share_link` | Get a share link by ID (includes `share_url`; uses `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` if set, otherwise `PAPERLESS_MCP_PAPERLESS_URL`) |
| `list_tasks` | List background tasks. Paginates (`page`, `page_size` up to 100). By default returns only unacknowledged tasks. Pass `include_acknowledged=True` to include acknowledged tasks, or `acknowledged=True` to return only acknowledged ones. |
| `get_task` | Get a task by ID |
| `wait_for_task` | Wait until a task completes |
| `get_statistics` | Get server statistics |
| `get_remote_version` | Get the Paperless-NGX version |

## Resources

| URI | Description |
|---|---|
| `config://paperless` | Server configuration snapshot |
| `stats://paperless` | Document statistics |
| `remote-version://paperless` | Paperless-NGX version |
| `tags://paperless` | All tags |
| `correspondents://paperless` | All correspondents |
| `document-types://paperless` | All document types |
| `custom-fields://paperless` | All custom fields |
| `storage-paths://paperless` | All storage paths |
| `saved-views://paperless` | All saved views |
| `tasks://paperless` | All background tasks |
| `paperless://documents/{document_id}` | Document by ID |
| `paperless://documents/{document_id}/content` | Extracted text content |
| `paperless://documents/{document_id}/metadata` | File metadata |
| `paperless://documents/{document_id}/notes` | Document notes |
| `paperless://documents/{document_id}/history` | Audit history |
| `paperless://documents/{document_id}/thumbnail` | Thumbnail image |
| `paperless://documents/{document_id}/preview` | PDF preview |
| `paperless://documents/{document_id}/download` | Original file download |

### Shared template variables

Inherited from `fastmcp-pvl-core` across all services built on the template:

<!-- GENERATED-ENV-TABLE-CORE-START — generated by scripts/gen_config_surface.py; do not edit -->
| Variable | Default | Description |
|---|---|---|
| `PAPERLESS_MCP_KV_STORE_URL` | `file:///data/state` | Persistent-state backend URL shared by every pvl-core subsystem that needs state. `memory://` is in-process and lost on restart; `file:///path` persists on one server; `redis://`, `dynamodb://` and `mongodb://` each need their matching extra. When unset, defaults to `file:///data/state` (the volume family Docker images mount), or to `memory://`; with a warning; on a host where that directory is not usable. |
| `FASTMCP_LOG_LEVEL` | `INFO` | Log level for FastMCP internals and app loggers (DEBUG / INFO / WARNING / ERROR / CRITICAL). The -v CLI flag overrides to DEBUG. |
| `FASTMCP_ENABLE_RICH_LOGGING` | `true` | Set false for plain or structured JSON log output. |
<!-- GENERATED-ENV-TABLE-CORE-END -->

Domain-specific variables go below under [Domain configuration](#domain-configuration).

## Authentication

Callers authenticate via a bearer token or OIDC (mutually exclusive). See the [Authentication guide](docs/guides/authentication.md) for setup, mapped multi-subject tokens, OIDC, and troubleshooting.

## Post-scaffold checklist

After `copier copy` and `gh repo create --push`:

1. **Fill in the DOMAIN blocks** (every section marked with a `DOMAIN` sentinel comment) in this README and in `CLAUDE.md`. The `GENERATED-ENV-TABLE-*` regions are not DOMAIN blocks; the config generator owns them and rewrites them on every run.
2. Configure GitHub secrets (see below).
3. Install dev + docs tooling: `uv sync --all-extras --all-groups`.
4. Install pre-commit hooks: `uv run pre-commit install`.
5. Run the gate locally: `uv run pytest -x -q && uv run ruff check --fix . && uv run ruff format . && uv run mypy src/ tests/`.
6. Push the first commit. CI should be green.
## GitHub secrets

CI workflows reference three repository secrets. Configure them via **Settings → Secrets and variables → Actions** or with `gh secret set`:

| Secret | Used by | How to generate |
|---|---|---|
| `RELEASE_TOKEN` | `release.yml`, `copier-update.yml`, `renovate.yml`, `bootstrap.yml` | Fine-grained PAT at <https://github.com/settings/personal-access-tokens/new> with `contents: write`, `pull_requests: write`, and `administration: write` (bootstrap sets branch protection + auto-merge). Scoped to this repo. |
| `CODECOV_TOKEN` | `ci.yml` | <https://codecov.io>: sign in with GitHub and add the repo. The upload token is on its settings page. |
| `CLAUDE_CODE_OAUTH_TOKEN` | `claude.yml`, `claude-code-review.yml` | Run `claude setup-token` locally and paste the result. |

```bash
gh secret set RELEASE_TOKEN
gh secret set CODECOV_TOKEN
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

> Dependency updates are handled by **Renovate** (`renovate.yml`), which reuses
> `RELEASE_TOKEN`. It maintains `uv.lock` and auto-merges patch/minor bumps once
> the `CI Success` check is green; `bootstrap.yml` enables auto-merge and branch
> protection on first push. GitHub Actions are updated in the copier template
> and arrive via `copier update`, not per-repo.

`GITHUB_TOKEN` is auto-provided; no action needed.

## Local development

The PR gate (matches CI):

```bash
uv run pytest -x -q                                  # tests
uv run ruff check --fix . && uv run ruff format .    # lint + format
uv run mypy src/ tests/                              # type-check
```

Pre-commit runs a subset of the gate on each commit; see `.pre-commit-config.yaml` for details, or [`CLAUDE.md`](CLAUDE.md) for the full Hard PR Acceptance Gates.

## Troubleshooting

### Moving a scaffolded project

`uv sync` creates `.venv/bin/*` scripts with absolute shebangs pointing at the venv Python. If you move the repo after scaffolding (`mv /old/path /new/path`), `uv run pytest` fails with `ModuleNotFoundError: No module named 'fastmcp'` because the stale shebang resolves to a different interpreter than the venv's site-packages.

**Fix:**

```bash
rm -rf .venv
uv sync --all-extras --all-groups
```

`uv run python -m pytest` also works as a one-shot workaround (bypasses the stale entry-script shim).

### `uv.lock` refresh after `copier update`

When `copier update` introduces new dependencies (such as a new extra added to `pyproject.toml.jinja`), the CI install step runs `uv sync --locked`, which fails against a stale lockfile. Run `uv lock` locally and commit the refreshed `uv.lock` alongside accepting the copier-update PR.

CI installs with `--locked` (and the review workflow with `--frozen`) so no job ever rewrites `uv.lock` in its own workspace: a job that re-locks hides the drift it just repaired, and a dirty workspace breaks any later `git checkout` in the same job. Lockfile drift then shows up as a red install step with a clear message, not as a silent mutation.

## Links

- [Documentation](https://pvliesdonk.github.io/paperless-mcp/)
- [llms.txt](https://pvliesdonk.github.io/paperless-mcp/llms.txt)
- [FastMCP](https://gofastmcp.com)
- [fastmcp-pvl-core](https://pypi.org/project/fastmcp-pvl-core/)

<!-- ===== TEMPLATE-OWNED SECTIONS END ===== -->

## Domain configuration

Domain environment variables use the `PAPERLESS_MCP_` prefix:

<!-- GENERATED-ENV-TABLE-DOMAIN-START — generated by scripts/gen_config_surface.py; do not edit -->
| Variable | Default | Required | Description |
|---|---|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | (none) | **Yes** | Base URL of the Paperless-NGX REST API, without a trailing slash. |
| `PAPERLESS_MCP_API_TOKEN` | (none) | **Yes** | Paperless service-account token used for outbound API requests. |
| `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` | `30.0` | No | Per-request HTTP timeout in seconds. |
| `PAPERLESS_MCP_HTTP_RETRIES` | `2` | No | Retries for idempotent requests after network errors or 5xx responses. |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` | `25` | No | Default page size for list tools, from 1 through 100. |
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | (none) | No | Public Paperless UI URL for user-visible links; defaults to PAPERLESS_URL. |
<!-- GENERATED-ENV-TABLE-DOMAIN-END -->

Domain-config fields are composed inside `src/paperless_mcp/config.py` between the `CONFIG-FIELDS-START` / `CONFIG-FIELDS-END` sentinels; env reads go through `fastmcp_pvl_core.env(_ENV_PREFIX, "SUFFIX", default)` so naming stays consistent, and field invariants go in `__post_init__` between the `CONFIG-VALIDATE-START` / `CONFIG-VALIDATE-END` sentinels. Each field's `metadata` `help` and `tags` generate the table above directly, so keep them accurate and complete.

## Key design decisions

<!-- DOMAIN-START -->
- **Read-only gating at startup, not per-call.** `PAPERLESS_MCP_READ_ONLY=true` skips registration of every mutating tool so they simply are not part of the advertised tool surface. Clients cannot invoke a write that will be refused.
- **HTTP layer retries idempotent reads only.** `PAPERLESS_MCP_HTTP_RETRIES` applies to GETs on 5xx/network errors; writes never retry automatically, to avoid double-applying bulk edits or uploads.
- **Tool icons come from `Lucide`.** Every tool carries a `Lucide` icon hint so MCP clients that render icons (Claude Desktop) get a coherent visual surface. See `src/paperless_mcp/tools/_icons.py`.
- **Models accept unknown upstream fields.** `Pydantic` models use lenient validation for list-endpoint responses so newer Paperless-NGX versions do not break the client (the `Document.some_future_paperless_field` test pins this behaviour).
- **No prompts ship in v1.** `prompts.py` is intentionally empty; prompts land as concrete user-workflow patterns emerge in practice.
<!-- DOMAIN-END -->
