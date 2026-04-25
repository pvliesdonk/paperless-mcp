# paperless-mcp — Design Spec

**Date:** 2026-04-23
**Status:** Approved (brainstorm phase complete, implementation plan pending)
**Author:** Peter van Liesdonk + Claude

## 1. Summary

A general-purpose, publishable FastMCP server that wraps the
[Paperless-NGX](https://docs.paperless-ngx.com/) REST API. Replaces the
community `paperless-mcp` project, which has been flaky on the MCP protocol
side and is not consistently maintained.

Built on [`fastmcp-server-template`](https://github.com/pvliesdonk/fastmcp-server-template)
(copier-based) and [`fastmcp-pvl-core`](https://github.com/pvliesdonk/fastmcp-pvl-core)
for shared infrastructure (auth, middleware, logging, server factory, artifact
store, CLI helpers). This is the **first greenfield use** of the template — any
friction becomes an upstream issue/PR rather than a local workaround.

### Identity

| Field | Value |
|---|---|
| GitHub repo | `pvliesdonk/paperless-mcp` |
| PyPI package | `pvliesdonk-paperless-mcp` |
| Python module | `paperless_mcp` |
| Console script | `paperless-mcp` |
| Env prefix | `PAPERLESS_MCP` |
| Human name | Paperless MCP |
| Docker image | `ghcr.io/pvliesdonk/paperless-mcp` |

### Design principles

1. **Faithful wrapper.** 1:1 mapping over Paperless REST. No Peter-specific
   assumptions about tag names or field IDs. Domain helpers (a possible future
   mode-C) live behind an optional module seam, not baked into core tools.
2. **Template adherence.** Prefer template-blessed patterns. Where
   `fastmcp-pvl-core` or the template doesn't obviously cover something:
   (a) write the minimum to unblock v1, (b) file an issue upstream describing
   the gap, (c) propose a PR if the solution is general.
3. **`copier update` clean.** Never modify template-owned files beyond clearly
   demarcated extension hooks. All domain logic in new files/modules.
4. **Pydantic-typed resources.** Strong types on everything we consume and
   everything we emit from tools; `extra="allow"` on inbound models so Paperless
   minor-version additions never break us.

## 2. Scope (v1)

**Writable (parity with existing community `paperless-mcp`):**
- Documents: list, search, get, upload, update, delete, download, thumbnail,
  content, bulk_edit, notes add/delete
- Tags / Correspondents / Document Types / Custom Fields: full CRUD
- Bulk-edit operations on tags/correspondents/document_types/custom_fields

**Read-only observability (additions):**
- Storage Paths, Saved Views, Share Links (read)
- Tasks (consume progress), Statistics, Remote Version
- Per-document: notes, metadata, history, suggestions

**Out of scope for v1** (safe to add in 0.x without breakage):
- Workflows CRUD
- Mail Accounts / Mail Rules
- Users / Groups write
- Trash operations (restore / permanent delete)
- UI Settings / Profile

**Read-only mode:** `PAPERLESS_MCP_READ_ONLY=true` disables every writable
tool, matching the template/pvl-core pattern.

## 3. Module layout

```
src/paperless_mcp/
  __init__.py              (template — untouched)
  cli.py                   (template — untouched)
  server.py                (template — untouched)
  config.py                (template — extended via additive DomainConfig)
  _server_apps.py          (template — untouched)
  _server_deps.py          (template — untouched)
  domain.py                (template slot — re-exports from client/)
  tools.py                 (template slot — calls register_all(mcp) from tools/)
  resources.py             (template slot — calls register_all(mcp) from resources/)
  prompts.py               (template slot — minimal v1)
  static/
    icons/                 (Lucide SVGs fetched from universal-icons MCP)

  client/                  (NEW — owned domain layer)
    __init__.py            (public API: PaperlessClient, exceptions)
    _http.py               (httpx.AsyncClient wrapper, auth, retry, pagination helper)
    _errors.py             (typed exceptions)
    documents.py
    tags.py
    correspondents.py
    document_types.py
    custom_fields.py
    storage_paths.py
    saved_views.py
    share_links.py
    tasks.py
    system.py              (statistics, remote_version)

  models/                  (NEW — pydantic resource models, extra="allow")
    __init__.py
    common.py              (Paginated[T], ListParams, BulkEditOperation enum, BulkEditResult, DownloadLink, UploadTaskAcknowledgement)
    document.py            (Document, DocumentNote, DocumentMetadata, DocumentHistoryEntry, DocumentSuggestions, DocumentPatch)
    tag.py
    correspondent.py
    document_type.py
    custom_field.py        (CustomField, CustomFieldInstance, CustomFieldDataType enum)
    storage_path.py
    saved_view.py
    share_link.py
    task.py                (Task, TaskStatus enum)
    system.py              (Statistics, RemoteVersion)

  tools/                   (NEW — one module per resource group)
    _icons.py              (ICON_REGISTRY: tool_name -> [Icon] data URI list)
    documents.py
    tags.py
    correspondents.py
    document_types.py
    custom_fields.py
    storage_paths.py
    saved_views.py
    share_links.py
    tasks.py
    system.py
    downloads.py           (create_download_link, get_document_thumbnail)

  resources/               (NEW — one module per URI group)
    documents.py           (paperless://documents/{id}/{variant})
    collections.py         (fixed: tags://, correspondents://, stats://, config://, etc.)
    tasks.py               (tasks://paperless)
```

**File ownership rules:**
- **Template-owned, untouched:** `__init__.py`, `cli.py`, `server.py`,
  `_server_apps.py`, `_server_deps.py`. `copier update --trust` must never
  produce conflicts on these.
- **Template slots (5-line dispatchers):** `tools.py`, `resources.py`,
  `prompts.py`, `domain.py`. Template owns the shape; we own the contents.
  Each file imports `register_all(mcp)` from its subpackage and nothing else.
- **Extended:** `config.py` — extension strategy TBD by implementation step 3
  (separate `DomainConfig` vs. editing `config.py`). If editing is required,
  this becomes a hybrid file and we file upstream issue #7.
- **New, fully owned:** `client/`, `models/`, `tools/`, `resources/`,
  `static/icons/`.

## 4. Tool surface

All tools get Lucide icons via the `universal-icons` MCP at build time
(fetched SVG → data URI list, baked into `static/icons/` and `tools/_icons.py`).
Read-only tools always registered; writable tools skipped when
`PAPERLESS_MCP_READ_ONLY=true`.

### Documents
- `list_documents(page=1, page_size=25, ordering=None, tags=None, correspondent=None, document_type=None, storage_path=None, custom_field=None, include_content=False) -> Paginated[Document]` — OCR `content` stripped by default; `notes[].note` and `custom_fields[].value` always stripped (see #30)
- `search_documents(query, page=1, page_size=25, more_like=None, include_content=False) -> Paginated[Document]` — same stripping as `list_documents`
- `get_document(id, include_content=False) -> Document` — OCR `content` stripped by default (#31); opt in for full text or use `get_document_content`
- `upload_document(filename, content_base64, title=None, correspondent=None, document_type=None, tags=None, created=None, archive_serial_number=None, custom_fields=None) -> UploadTaskAcknowledgement`
- `update_document(id, patch: DocumentPatch, include_content=False) -> Document` — response OCR `content` stripped by default
- `delete_document(id) -> None`
- `bulk_edit_documents(document_ids, method, parameters) -> BulkEditResult`
- `get_document_content(id) -> str` — OCR'd plain text
- `get_document_thumbnail(id) -> ImageContent` — small PNG, inline
- `get_document_notes(id) -> list[DocumentNote]`
- `add_document_note(id, note) -> DocumentNote`
- `delete_document_note(id, note_id) -> None`
- `get_document_metadata(id) -> DocumentMetadata`
- `get_document_history(id) -> list[DocumentHistoryEntry]`
- `get_document_suggestions(id) -> DocumentSuggestions`

### Tags / Correspondents / Document Types / Custom Fields
Each gets the standard quintet:
- `list_{resource}(page=1, page_size=100, ordering=None, name__icontains=None) -> Paginated[T]`
- `get_{resource}(id) -> T`
- `create_{resource}(body: TCreate) -> T`
- `update_{resource}(id, patch: TPatch) -> T`
- `delete_{resource}(id) -> None`

### Bulk admin
- `bulk_edit_tags(operation, ids, **params) -> BulkEditResult`
- `bulk_edit_correspondents(operation, ids, **params) -> BulkEditResult`
- `bulk_edit_document_types(operation, ids, **params) -> BulkEditResult`

Custom fields are intentionally excluded: Paperless-NGX's `bulk_edit_objects`
endpoint does not accept `object_type=custom_fields` (see issue #38).

### Read-only observability
- `list_storage_paths(...)`, `get_storage_path(id)`
- `list_saved_views(...)`, `get_saved_view(id)`
- `list_share_links(document_id=None)`, `get_share_link(id)`
- `list_tasks(status=None, acknowledged=None)`, `get_task(uuid)`,
  `wait_for_task(uuid, timeout_seconds=60)` — convenience poller
- `get_statistics() -> Statistics`
- `get_remote_version() -> RemoteVersion`

### Downloads
- `create_download_link(document_id, variant: Literal["original","archived","preview"]="original", ttl_seconds=300) -> DownloadLink`
  — backed by pvl-core `ArtifactStore`. Returns
  `{download_url, expires_in_seconds, content_type, filename}`. HTTP/SSE
  transport only; raises a clear error on stdio.

## 5. Resource surface

### Fixed URIs (collection-level JSON)
- `config://paperless` — effective config (no secrets)
- `stats://paperless` — Paperless `/api/statistics/`
- `remote_version://paperless` — `/api/remote_version/`
- `tags://paperless`, `correspondents://paperless`, `document_types://paperless`,
  `custom_fields://paperless`, `storage_paths://paperless`,
  `saved_views://paperless`
- `tasks://paperless` — recent tasks, capped, newest first

### Templated URIs (per-document)
- `paperless://documents/{id}` — Document JSON
- `paperless://documents/{id}/content` — OCR'd text (text/plain)
- `paperless://documents/{id}/metadata` — metadata JSON
- `paperless://documents/{id}/notes` — notes JSON
- `paperless://documents/{id}/history` — audit history JSON
- `paperless://documents/{id}/thumbnail` — small PNG (image/png)
- `paperless://documents/{id}/preview` — rendered preview (PDF or image)
- `paperless://documents/{id}/download` — original file bytes

### Templated URIs (per-entity)
- `paperless://tags/{id}`, `paperless://correspondents/{id}`,
  `paperless://document_types/{id}`, `paperless://custom_fields/{id}`,
  `paperless://storage_paths/{id}`, `paperless://saved_views/{id}`,
  `paperless://share_links/{id}`, `paperless://tasks/{uuid}`

### Binary-content policy
- **Thumbnails:** resource (image/png) **and** `get_document_thumbnail` tool
  returning `ImageContent` for inline LLM visibility.
- **Preview / download:** resource only — never tool return. LLM-facing
  delivery goes via `create_download_link` (one-time unauthenticated URL).
- **OCR content:** resource **and** tool (`get_document_content`) — plain text
  is safe inline.

### Discoverability
`list_resources` (auto-generated by FastMCP) exposes only fixed URIs plus
templated URI patterns — never enumerates per-document URIs.

## 6. Configuration

### Template-provided env vars (inherited unchanged)
- `PAPERLESS_MCP_TRANSPORT` — `http` | `stdio`
- `PAPERLESS_MCP_HOST` / `PORT` / `HTTP_PATH`
- `PAPERLESS_MCP_BASE_URL` — public base URL
- `PAPERLESS_MCP_LOG_LEVEL`, `LOG_FORMAT`
- `PAPERLESS_MCP_OIDC_*` — full OIDC proxy block (`CONFIG_URL`, `CLIENT_ID`,
  `CLIENT_SECRET`, `AUDIENCE`, `REQUIRED_SCOPES`, `JWT_SIGNING_KEY`,
  `VERIFY_ACCESS_TOKEN`)
- `PAPERLESS_MCP_BEARER_TOKEN` — alternative to OIDC
- `PAPERLESS_MCP_READ_ONLY` — gates writable tools
- `PAPERLESS_MCP_INSTRUCTIONS` — operator-supplied domain description

### Domain-specific env vars (added via `DomainConfig`)
- `PAPERLESS_MCP_PAPERLESS_URL` (required) — e.g. `http://paperless-ngx:8000`
- `PAPERLESS_MCP_API_TOKEN` (required) — Paperless service-account token
- `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` (default `30`, per-request)
- `PAPERLESS_MCP_HTTP_RETRIES` (default `2`, only on connect/5xx)
- `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` (default `300`,
  clamped `[30, 3600]`)
- `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` (default `25`, max `100`)

### Secrets handling
`PAPERLESS_MCP_API_TOKEN` is never surfaced in `config://paperless` or logs.
Masking lives in `_http.py` log sanitizer. Candidate for upstream (issue #8).

## 7. HTTP client & models

### `client/_http.py`
- `httpx.AsyncClient` with persistent session, `Authorization: Token {API_TOKEN}`
  header, `Accept: application/json; version=9` (pin Paperless API version).
- Typed errors: `NotFoundError` (404), `AuthError` (401/403),
  `ConflictError` (409), `ValidationError` (400), `RateLimitError` (429),
  `UpstreamError` (5xx), `PaperlessAPIError` (base).
- Retry: network/5xx only, exponential backoff, up to `HTTP_RETRIES` retries
  (not counting the initial attempt), idempotent methods only.
- Internal pagination helper: `paginate(url, params) -> AsyncIterator[T]`
  (used by resource handlers that need to walk all entities). Tools return
  raw `Paginated[T]` — no auto-walk.
- Request/response logging at DEBUG with secret masking.

### Pydantic models
- `extra="allow"` on all **inbound** (Paperless → us) models.
- Strict (no `extra`) on all **outbound** (us → Paperless) models like
  `DocumentPatch`, `TagCreate`, `TagPatch` — unknown fields are bugs.
- Enums: `CustomFieldDataType`, `TaskStatus`, `BulkEditOperation`,
  `ShareLinkFileVersion`.
- `Paginated[T]`: `count`, `next`, `previous`, `results: list[T]`. The upstream `all: [...]` id array is dropped (#25). `next`/`previous` are normalised to bare `page=N` markers (or `None`) regardless of whether Paperless returns a full URL or a client-paginated endpoint emits the marker directly — the internal Paperless hostname never leaks into MCP responses (#32).

### Instructions block
Built via pvl-core `build_instructions()`. Domain description from
`PAPERLESS_MCP_INSTRUCTIONS` env override or default: _"Paperless-NGX document
management over MCP: search, tag, upload, and read documents; manage tags,
correspondents, document types, and custom fields. Paths and IDs are
Paperless-side."_ Read-only state is appended automatically by pvl-core.

## 8. Testing & packaging

### Test tiers
1. **Unit tests for `client/` and `models/`** — `respx` intercepts `httpx`.
   Fixtures: recorded JSON from a real Paperless instance, PII pruned,
   in `tests/fixtures/paperless/`. Per-module coverage of happy path, 404,
   401, 400, pagination, and unknown-field round-trip (`extra="allow"`).
2. **Tool/resource registration tests** — in-process FastMCP server; assert
   every tool and resource is registered with expected name, annotations, and
   icon list; assert read-only mode omits the right tools.
3. **End-to-end contract tests** (`@pytest.mark.integration`, skipped without
   `PAPERLESS_MCP_IT_URL` + `PAPERLESS_MCP_IT_TOKEN`) — disposable Paperless
   instance in CI: upload → tag → search → download → delete.
4. **Download-link tests** — `ArtifactStore`-backed URL serves right bytes
   with right `Content-Type`, 404s after first fetch or TTL expiry, raises
   clearly under stdio.

### Packaging
- Template-generated `pyproject.toml`, `hatchling` backend, Python `>=3.11`.
- Core deps: `fastmcp-pvl-core`, `httpx`, `pydantic`, `pydantic-settings`.
- Optional deps: `dev` (pytest, respx, ruff, mypy), `docs` (mkdocs-material,
  mkdocstrings).
- `ruff` + `mypy --strict` on domain modules; template-owned files use the
  template's lint config via `overrides`.

### Docker / compose
- Template `Dockerfile` and `compose.yml` untouched.
- Downstream wiring into `40-documents/compose.yml` deferred; copyable
  `examples/compose.yml` snippet included for future use.

### Docs
- Template's mkdocs setup → `pvliesdonk.github.io/paperless-mcp/`.
- `docs/tools/`, `docs/resources/` auto-indexed from docstrings.
- `docs/design.md` = this spec.

### CI
- Template-provided: ruff, mypy, gitleaks pre-commit; GH Actions lint + unit
  on push, integration gated behind a repo secret, docs build,
  semantic-release on main.

## 9. Build sequence

1. **Scaffold.** `copier copy gh:pvliesdonk/fastmcp-server-template paperless-mcp`
   with the identity values from §1. Verify `uv sync`, `uv run pytest`,
   `uv run paperless-mcp --help` pass on vanilla scaffold.
2. **Initialize git, push empty repo.** Verify GH Actions pass on a pristine
   scaffold to catch template regressions early.
3. **Domain config.** Add `DomainConfig`. If editing `config.py` is required,
   file upstream issue #7 before proceeding.
4. **HTTP client + errors.** `client/_http.py`, `client/_errors.py`.
5. **Pydantic models.** `models/*` with `respx`-backed round-trip tests.
6. **Read-only client methods.** `client/*.py` (read methods only).
7. **Write client methods.** CRUD writes, upload, bulk_edit.
8. **Icons.** Fetch Lucide via `universal-icons` MCP, generate `tools/_icons.py`.
   If pvl-core lacks a registration helper, hand-roll and file upstream #3.
9. **Tool layer.** `tools/*` + `tools.py` dispatcher. Read-only gating —
   if pvl-core lacks it, hand-roll and file upstream #1.
10. **Resource layer.** `resources/*` + `resources.py` dispatcher. Fixed URIs
    first, templated URIs second.
11. **Download links.** `tools/downloads.py`. Validates `ArtifactStore`
    contract; if assumptions fail, file upstream #4 before proceeding.
12. **Instructions, server metadata, prompts.** Minimal v1 prompts.
13. **Integration test suite.**
14. **Docs pass.** `docs/design.md`, README env-var table, `examples/compose.yml`.
15. **Release 0.1.0** via semantic-release.

## 10. Upstream candidates (consolidated)

Filed against `fastmcp-pvl-core` unless noted. Items 1, 3, 4, 7 are
blocking/near-blocking and filed during the build; the rest are nice-to-have
PRs post-v1.

1. Read-only mode gating helper — decorator or context for conditional tool
   registration.
2. Generic `Paginated[T]` model + paginate helper — reusable across any
   REST-wrapping server.
3. Icon registration helper — resolve SVG files under `static/` to data URIs,
   wire to tools.
4. `ArtifactStore.put_ephemeral(bytes, content_type, ttl) -> URL` contract —
   confirm signature matches need; may be a doc PR only.
5. Resource-URL registration by prefix — ergonomics.
6. Resource + tool pair registration — binary content idiom.
7. Domain-config extension hook — documented way to add env vars without
   editing `config.py`.
8. Secret-masking log filter — reusable across any server with an API token.
9. Pydantic version alignment doc — downstream guidance.
10. `@live_integration` pytest marker + fixture — opt-in live backend tests.
11. mkdocs tool-page autogen pattern — confirm standard plugin or document
    convention.

## 11. Open questions deferred to implementation

None blocking — all open points above are tracked as upstream candidates and
resolved during the build sequence. Future mode-C (domain helpers) is
explicitly out of scope for v1.
