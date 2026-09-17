# Reference research log

## 2026-09-17

- Added [Who may read an MCP resource](mcp-resource-access.md), read from the
  MCP 2025-06-18 resources specification, FastMCP's `ResourcesAsTools` page,
  and the running Claude Code host's own tool schemas. Written during review of
  [#114](https://github.com/pvliesdonk/paperless-mcp/issues/114), whose first
  draft told the model to "read `paperless://documents/<id>`". The spec settles
  it: `resources/read` is a client-to-server request and resources are
  "application-driven", so the model is never the protocol actor — but the same
  section permits a host to include context by "the AI model's selection",
  which is what Claude Code's `ReadMcpResourceTool` implements. That is the
  trap worth recording: resource-reading prose tests clean on this host
  precisely because this host grants an affordance the protocol does not
  require, so testing here cannot tell you whether the prose is portable.
  The Claude Code claim rests on in-session tool schemas rather than the
  published MCP page, which documents configuration and tools but not the
  resource interaction model; the page says so rather than citing a doc that
  does not make the claim.
- Added [Paperless-NGX API payload versions 9 and 10](paperless-api-versioning.md)
  and [The Paperless-NGX 3.x REST surface this server does not expose](paperless-3x-rest-surface.md),
  read from paperless-ngx at `d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e` (the
  `v3.1.3` tag), from its `docs/api.md`, from `v2.20.15` for the 2.x accepted
  versions, and from a live 3.1.3 instance. Written for
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113), which asked
  what 3.x adds and what payload version 10 changes. Note that the 2026-09-16
  pass recorded `ae9529551d17395c69dedf63a4472b45df0dab0f` as "3.1.3" while
  the `v3.1.3` tag resolves to `d48663e9…`, so the two passes pin different
  commits and only this one pins the release. The difference is exactly one
  commit — `ae95295` is the tag plus "Documentation: Add v3.1.3 changelog",
  which touches no source file — so no line that page cites can have moved,
  and its `subject_version` is left as it stands rather than corrected.
- The instance's own OpenAPI document is vendored into the bundle as
  `paperless-openapi-3.1.3.json.gz` with a plain-text route list beside it,
  because it is the only complete description of the 3.x surface —
  `docs/api.md` documents neither chat nor AI suggestions. Storing it makes
  the next refresh a diff instead of a re-derivation. It is committed
  compressed to stay under the repository's 500 KB added-file limit, and was
  checked for hostnames, credentials and archive content before committing.
- The sweep answered the issue's central question against a live AI-enabled
  instance rather than by inference: `/api/documents/{id}/suggestions/` does
  **not** become AI-backed when AI is enabled. AI suggestions are a separate
  route, and the classic handler reads no AI configuration at all.
- The refute pass caught an overclaim of my own making. The first draft said
  fifteen of seventeen endpoints were identical across versions, but the
  key-set comparison had silently skipped `saved_views`, `share_links` and
  `storage_paths`, all empty on the instance — and saved views are precisely
  where a documented difference lives (`show_on_dashboard`, `show_in_sidebar`
  at version 9 only). Those claims are now sourced and marked `[unverified]`
  as unreproduced. The same pass added a value-level comparison, because a
  key-set diff cannot see the document `created` change `api.md` describes;
  that one turned out to have no runtime branch at 3.1.3.
- Two naming traps are recorded rather than left to be rediscovered: the chat
  route is `/api/documents/chat/`, and `/api/chat/` redirects to a login page
  rather than 404ing; and `src/documents/versioning.py` is about document
  versions, not API payload versions.
- A second, independent pass re-found all fifteen load-bearing `[source: ...]`
  citations against fresh checkouts of `v3.1.3` and `v2.20.15`, reading the
  code rather than trusting the pass that wrote the claims — which is what the
  `verified` entry on both pages attests. No claim mismatched and no cited
  range was wrong. Two refinements came out of it and are folded in: the
  version 10 task filters are *silently dropped* rather than rejected, and the
  `ai_suggestions` 503 is absent from the OpenAPI document, so the vendored
  spec under-describes that endpoint's failure modes. Next review: 2027-03-17.

## 2026-09-16

- Added [Paperless-NGX version endpoints](paperless-version-endpoints.md),
  read from paperless-ngx at `ae9529551d17395c69dedf63a4472b45df0dab0f`
  (3.1.3) and from Django REST framework's permissions guide. Covered what
  `/api/remote_version/`, `/api/ui_settings/` and `/api/status/` each report
  for the version, where each value originates inside Paperless, and the
  permission each call costs. Written for
  [#123](https://github.com/pvliesdonk/paperless-mcp/issues/123), where four
  surfaces described the newest published release as the connected instance's
  version.
- The refute pass corrected one claim carried over from the issue: the
  remote-version endpoint is not merely "less gated" than `ui_settings`, it is
  permission-ungated, because `RemoteVersionView` declares no
  `permission_classes` and the project sets no `DEFAULT_PERMISSION_CLASSES`,
  leaving DRF's `AllowAny` default in force. Paperless 2.x handlers were not
  re-read and are marked as not covered. Next review: 2027-03-16.

## 2026-09-12

- Added [GitHub planning objects](github-planning-objects.md), checked
  against GitHub.com documentation and GitHub CLI 2.97.0. Covered milestone
  identity, pagination, PR membership, nullable updates, issue hierarchy and
  dependencies, and documented attachment support. Refute pass retained the
  cross-owner REST documentation conflict and marked unreproduced UI/search
  observations explicitly. Next review: 2027-03-12.
