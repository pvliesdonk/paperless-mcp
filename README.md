<!-- DOMAIN-START -->
<!-- Add an optional project logo or project-specific header here. Kept across copier update. -->
<!-- DOMAIN-END -->

# Paperless MCP

<!-- mcp-name: io.github.pvliesdonk/paperless-mcp -->

[![CI](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/pvliesdonk/paperless-mcp/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/pvliesdonk/paperless-mcp/graph/badge.svg)](https://codecov.io/gh/pvliesdonk/paperless-mcp) [![repowise](https://api.repowise.dev/badge/wiki/pvliesdonk/paperless-mcp.svg)](https://repowise.dev/repo/pvliesdonk/paperless-mcp) [![Code health](https://api.repowise.dev/badge/health/pvliesdonk/paperless-mcp.svg)](https://repowise.dev/repo/pvliesdonk/paperless-mcp) [![PyPI](https://img.shields.io/pypi/v/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![Python](https://img.shields.io/pypi/pyversions/pvliesdonk-paperless-mcp)](https://pypi.org/project/pvliesdonk-paperless-mcp/) [![License](https://img.shields.io/github/license/pvliesdonk/paperless-mcp)](LICENSE) [![Docker](https://img.shields.io/github/v/release/pvliesdonk/paperless-mcp?label=ghcr.io&logo=docker)](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://pvliesdonk.github.io/paperless-mcp/) [![llms.txt](https://img.shields.io/badge/llms.txt-available-brightgreen)](https://pvliesdonk.github.io/paperless-mcp/latest/llms.txt) [![Template](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/pvliesdonk/paperless-mcp/main/.copier-answers.yml&query=%24._commit&label=template)](https://github.com/pvliesdonk/fastmcp-server-template)

Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.

**[Documentation](https://pvliesdonk.github.io/paperless-mcp/)** | **[Config wizard](https://pvliesdonk.github.io/paperless-mcp/latest/configuration-generator/)** | **[PyPI](https://pypi.org/project/pvliesdonk-paperless-mcp/)** | **[Docker](https://github.com/pvliesdonk/paperless-mcp/pkgs/container/paperless-mcp)**

## Features

<!-- DOMAIN-START -->
- **File transfer links:** Download document files and full OCR Markdown over HTTP. Upload files, including Markdown, through the same transfer route. Set `PAPERLESS_MCP_BASE_URL` to enable the tools. File bytes stay outside model context. See [file transfer links](docs/tools/index.md#file-transfer-links).
- **Document search & retrieval:** full-text and filtered list queries against Paperless-NGX, plus access to extracted OCR text, metadata, and thumbnails.
- **Tag, correspondent, document-type, custom-field management:** full CRUD and bulk-edit for every classification dimension Paperless exposes.
- **Document lifecycle** supports uploads, field changes, notes, audit history, and AI-suggested tags/correspondents/types.
- **Operational introspection** covers saved views, storage paths, share links, background tasks (with `wait_for_task`), statistics, and an upstream release check for Paperless-NGX.
- **MCP tools:** 49 LLM-visible tools with `Lucide` icons; see `src/paperless_mcp/tools/`.
- **MCP resources:** 16 URIs exposing bounded document previews and domain collections; see `src/paperless_mcp/resources/`.
<!-- DOMAIN-END -->

## What you can do with it

<!-- DOMAIN-START -->
With this server mounted in an MCP client (Claude, etc.), you can:

- **"Find last quarter's invoices from ACME."** Composes `search_documents` with a correspondent filter, then reads bounded previews with `get_document_content`.
- **"Tag these three documents as 'reviewed' and move them to the Accounting correspondent."** Uses `bulk_edit_documents` in a single call.
- **"Upload this PDF and wait until OCR finishes."** Composes `upload_document` + `wait_for_task` so the assistant only reports back once the document is indexed.
- **"What changed on document 4213 in the last week?"** Reads `paperless://documents/4213/history` and summarises the audit trail.

Every tool and resource is listed in the documentation site: [Tools](https://pvliesdonk.github.io/paperless-mcp/latest/tools/) and [Resources](https://pvliesdonk.github.io/paperless-mcp/latest/resources/). The Paperless variables the server reads are in [Configuration](https://pvliesdonk.github.io/paperless-mcp/latest/configuration/).
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

To run the newest merged code instead of the newest release, use the rolling `edge` tag. It is rebuilt on every merge to `main` and carries no version identity. See [Image tags](docs/deployment/docker.md#image-tags) for the full tag list.

```bash
docker pull ghcr.io/pvliesdonk/paperless-mcp:edge
```

A `compose.yml` ships at the repo root and runs as-is: copy `.env.example` to `.env`, then `docker compose up -d`. It publishes port 8000 on the host and assumes no reverse proxy; [Docker Compose](docs/deployment/docker.md#docker-compose) covers the configuration split, the domain sentinel blocks, and a Traefik overlay.

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

## Release channels

Artifacts ship on three channels. Each row lists exactly what that channel publishes.

| Channel | Version identity | Artifacts |
|---|---|---|
| `edge` (rolling) | None; the commit is the identity | Docker image `:edge` rebuilt on every merge to `main`; `.mcpb` bundle as the `mcpb-bundle-edge` workflow artifact; Claude Code plugin `.zip` as the `plugin-zip-edge` artifact; rolling `unstable` docs version. It leaves no git tag, GitHub release, or PyPI entry behind. |
| Pre-release | `vX.Y.Z-rc.N`, computed and reviewed in its release pull request | PyPI (as the pre-release `X.Y.ZrcN`); GitHub release with wheels, `sdist`, `.deb`/`.rpm` packages, `.mcpb` bundle, plugin `.zip`, and SBOM attached; Docker image under its immutable `vX.Y.Z-rc.N` tag plus the ordering-aware rolling `rc` tag. Skips the plugin marketplace, the MCP registry, and the docs deploy. |
| Stable | `vX.Y.Z` | Everything: PyPI, Docker (version tag plus ordering-aware `latest` / `vX` / `vX.Y`), `.deb`/`.rpm`, GitHub release assets (wheels, `sdist`, `.mcpb` bundle, plugin `.zip`, SBOM), plugin marketplace and MCP registry entries (when the release is the newest stable), versioned docs with an ordering-aware `latest` alias. |

Pre-releases reach PyPI so that a candidate's `.mcpb` bundle installs: the bundle points at PyPI rather than carrying the code. Ordinary installers never see them, because a PEP 440 resolver skips pre-releases unless the requirement pins one or you pass `--pre`. Ask for a candidate by name with `pip install pvliesdonk-paperless-mcp==X.Y.ZrcN`. PyPI spells it in the PEP 440 canonical form, while tags use SemVer. Rolling pointers are ordering-aware, so a patch release cut from an old `release/X.Y` branch never moves `latest`-style tags back to older content, and a candidate for an already-released version never moves `rc`. See [Release process](docs/deployment/release-process.md) for the full model.

## Quick start

```bash
paperless-mcp serve                                # stdio transport
paperless-mcp serve --transport http --port 8000   # streamable HTTP
```

For library usage (embedding the domain logic without the MCP transport), import from the `paperless_mcp` package directly. See the project's domain modules under `src/paperless_mcp/` for entry points.

### Server info

The server registers a built-in `get_server_info` tool (via `fastmcp_pvl_core.register_server_info_tool`) so operators can confirm the deployed version with a single MCP call. The default response carries `server_name`, `server_version`, and `core_version`. Servers that talk to a remote upstream wire upstream version reporting inside the `DOMAIN-UPSTREAM-START` / `DOMAIN-UPSTREAM-END` sentinel in `src/paperless_mcp/server.py`; see [`tool-registration`](.agents/skills/tool-registration/SKILL.md#server-info-tool-get_server_info) for the wiring pattern.

### Health

The server serves `/health` (liveness, a static `200`) and `/health/ready` (readiness, `503` when a backing store or a domain check fails) outside the MCP mount and outside auth, via `fastmcp_pvl_core.register_health_routes`. `compose.yml` probes the first. Domain readiness checks go in the `health_checks` dict in `src/paperless_mcp/server.py`; see [Docker deployment](docs/deployment/docker.md#health) for the routes, the mount-path rule, and `PAPERLESS_MCP_HEALTH_DETAIL`.

## Configuration

The most common environment variables, shared across all
`fastmcp-pvl-core`-based services:

<!-- GENERATED-ENV-TABLE-CORE-START — generated by scripts/gen_config_surface.py; do not edit -->
| Variable | Default | Description |
|---|---|---|
| `PAPERLESS_MCP_KV_STORE_URL` | `file:///data/state` | Persistent-state backend URL shared by every pvl-core subsystem that needs state. `memory://` is in-process and lost on restart; `file:///path` persists on one server; `redis://`, `dynamodb://` and `mongodb://` each need their matching extra. When unset, defaults to `file:///data/state` (the volume family Docker images mount), or to `memory://` (with a warning) on a host where that directory is not usable. |
| `PAPERLESS_MCP_LOG_LEVEL` | `INFO` | Log level for every logger in the process, FastMCP's included (DEBUG / INFO / WARNING / ERROR / CRITICAL). The -v CLI flag overrides to DEBUG. The unprefixed FASTMCP_LOG_LEVEL still works for one major version and logs a deprecation warning. |
| `PAPERLESS_MCP_LOG_FORMAT` | (none) | Log rendering. rich is one colour event key=value line per record, for a terminal; json is one JSON object per record, for a collector. Unset picks rich when stderr is a terminal and json everywhere else, so a container or journald gets JSON with no configuration. |
<!-- GENERATED-ENV-TABLE-CORE-END -->

This table and the one under [Domain configuration](#domain-configuration)
are curated subsets. The complete generated reference, with every variable
the server reads, is the [configuration reference](docs/configuration.md);
`.env.example` lists the same surface in copy-paste form.

## Authentication

Callers authenticate via a bearer token or OIDC (mutually exclusive). See the [Authentication guide](docs/guides/authentication.md) for setup, mapped multi-subject tokens, OIDC, and troubleshooting.

## Post-scaffold checklist

After `copier copy` and `gh repo create --push`:

1. **Fill in the DOMAIN blocks** (every section marked with a `DOMAIN` sentinel comment) in this README and in `AGENTS.md`. The `GENERATED-ENV-TABLE-*` regions are not DOMAIN blocks; the config generator owns them and rewrites them on every run.
2. Configure GitHub secrets (see below).
3. Install dev + docs tooling: `uv sync --all-extras --all-groups`.
4. Install pre-commit hooks: `uv run pre-commit install`.
5. Run the gate locally: `uv run pytest -x -q && uv run ruff check --fix . && uv run ruff format . && uv run mypy src/ tests/`.
6. Push the first commit. CI should be green.

## GitHub secrets

CI workflows reference two required repository secrets and one optional Claude token. Configure them via **Settings → Secrets and variables → Actions** or with `gh secret set`:

| Secret | Used by | How to generate |
|---|---|---|
| `RELEASE_TOKEN` | `release-prepare.yml`, `release.yml`, `copier-update.yml`, `renovate.yml`, `bootstrap.yml` | Fine-grained PAT at <https://github.com/settings/personal-access-tokens/new> with `contents: write`, `pull_requests: write`, and `administration: write` (bootstrap applies the repository rulesets, auto-merge, and the security settings). Must belong to a repository admin: the shipped rulesets grant bypass to the admin role, and the release tag + GitHub release that knope creates after a release pull request merges rely on it (pull requests the token opens also need it so their CI runs). Scoped to this repo. |
| `CODECOV_TOKEN` | `ci.yml` | <https://codecov.io>: sign in with GitHub and add the repo. The upload token is on its settings page. |
| `CLAUDE_CODE_OAUTH_TOKEN` | `claude.yml` | Optional. Run `claude setup-token` locally and configure this only for `@claude` or opted-in automatic review. |

```bash
gh secret set RELEASE_TOKEN
gh secret set CODECOV_TOKEN
# Optional: enables @claude and opted-in automatic review.
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

> Dependency updates are handled by **Renovate** (`renovate.yml`), which reuses
> `RELEASE_TOKEN`. It maintains `uv.lock` and auto-merges patch/minor bumps once
> the `CI Success` check is green; `bootstrap.yml` enables auto-merge, applies
> the repository rulesets (`.github/rulesets/`), and turns on private
> vulnerability reporting and Dependabot alerts on first push. See
> [Repository Protection](docs/deployment/repository-protection.md) for the
> per-branch posture, bypass model, and security settings. GitHub Actions are updated in the copier
> template and arrive via `copier update`, not per-repo.

`GITHUB_TOKEN` is auto-provided; no action needed.

## Local development

The PR gate (matches CI):

```bash
uv run pytest -x -q                                  # tests
uv run ruff check --fix . && uv run ruff format .    # lint + format
uv run mypy src/ tests/                              # type-check
```

Pre-commit runs a subset of the gate on each commit; see `.pre-commit-config.yaml` for details, or [`AGENTS.md`](AGENTS.md) for the full Hard PR Acceptance Gates.

CI requires tests to pass on Python 3.11 through 3.14. Python 3.14 also collects
branch coverage and enforces the 80% total and patch coverage thresholds.
To reproduce that test command, run
`uv run --python 3.14 pytest --cov --cov-report=xml --durations=20`.

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

## Contributing

`CONTRIBUTING.md` holds the rules for issues and pull requests, and where a
fix belongs: `fastmcp-pvl-core` for library code, the template for
template-owned files, this repository for anything inside its `DOMAIN-*` /
`CONFIG-*` / `PROJECT-*` blocks. `AGENTS.md` carries the conventions and
gates; the skills under `.agents/skills/` carry the task procedures, among
them `code-review` (local self-review before a pull request),
`writing-release-notes` (release notes),
`applying-template-updates` (the weekly template update pull request) and
`authoring-issues-prs` (filing). The release procedure is in
[docs/deployment/release-process.md](docs/deployment/release-process.md);
the template update procedure in
[docs/deployment/template-updates.md](docs/deployment/template-updates.md).
`SECURITY.md` says how to report a vulnerability privately, and what to
expect after.

## Links

- [Documentation](https://pvliesdonk.github.io/paperless-mcp/)
- [llms.txt](https://pvliesdonk.github.io/paperless-mcp/latest/llms.txt)
- [FastMCP](https://gofastmcp.com)
- [fastmcp-pvl-core](https://pypi.org/project/fastmcp-pvl-core/)

<!-- ===== TEMPLATE-OWNED SECTIONS END ===== -->

## Domain configuration

The variables this project features as its entry points (domain variables use the `PAPERLESS_MCP_` prefix):

<!-- GENERATED-ENV-TABLE-DOMAIN-START — generated by scripts/gen_config_surface.py; do not edit -->
| Variable | Default | Required | Description |
|---|---|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | (none) | No | Base URL of the Paperless-NGX REST API, without a trailing slash. The server refuses to start without it. |
| `PAPERLESS_MCP_API_TOKEN` | (none) | No | Paperless service-account token used for outbound API requests. The server refuses to start without it. |
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | (none) | No | Public Paperless UI URL for user-visible links; defaults to PAPERLESS_URL. |
<!-- GENERATED-ENV-TABLE-DOMAIN-END -->

This is a curated subset: a field appears here when its `tags` metadata includes `readme`. Every domain variable is documented in the [configuration reference](docs/configuration.md), grouped the same way the config wizard presents them.

Domain-config fields are composed inside `src/paperless_mcp/config.py` between the `CONFIG-FIELDS-START` / `CONFIG-FIELDS-END` sentinels; env reads go through `fastmcp_pvl_core.env(_ENV_PREFIX, "SUFFIX", default)` so naming stays consistent, and field invariants go in `__post_init__` between the `CONFIG-VALIDATE-START` / `CONFIG-VALIDATE-END` sentinels. Each field's `metadata` `help`, `tags`, and `wizard` group generate the reference tables directly, so keep them accurate and complete.

## Key design decisions

<!-- DOMAIN-START -->
- **Read-only deployments use tool visibility, not a domain switch.** Set `PAPERLESS_MCP_TOOLS_DENY` (or `PAPERLESS_MCP_TOOLS_ALLOW`) to hide the mutating tools, including `create_upload_link` when transfers are enabled. The template applies visibility last in `make_server`, so hidden tools leave `tools/list` and are rejected on `tools/call`. Clients cannot invoke a write that will be refused, and the rule lives in one place for every server built on this template.
- **HTTP layer retries idempotent reads only.** `PAPERLESS_MCP_HTTP_RETRIES` applies to GETs on 5xx/network errors; writes never retry automatically, to avoid double-applying bulk edits or uploads.
- **Tool icons come from `Lucide`.** Every tool carries a `Lucide` icon hint so MCP clients that render icons (Claude Desktop) get a coherent visual surface. See `src/paperless_mcp/tools/_icons.py`.
- **Paperless API compatibility:** requests prefer payload version 10, with automatic version 9 fallback for Paperless 2.x after an explicit version rejection. Tasks include structured results and timing data while retaining the legacy fields. Saved-view visibility flags can now be `null`; Python consumers must handle that value. See [task tools](docs/tools/index.md#task-tools).
- **Models accept unknown upstream fields.** `Pydantic` models use lenient validation for list-endpoint responses so newer Paperless-NGX versions do not break the client (the `Document.some_future_paperless_field` test pins this behaviour).
- **No prompts ship in v1.** `prompts.py` is intentionally empty; prompts land as concrete user-workflow patterns emerge in practice.
<!-- DOMAIN-END -->
