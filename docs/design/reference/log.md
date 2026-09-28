# Reference research log

## 2026-09-27

- Extended [bulk edit and deferred search indexing](paperless-bulk-edit-indexing.md)
  with the methods and fields each endpoint accepts, read from Paperless 3.1.3
  `serialisers.py` and `views.py`, 2.20.15 `serialisers.py` and the vendored
  3.1.3 OpenAPI document. Found two project bugs: `redo_ocr` is not a 3.x
  method (2.x aliased it to `reprocess`), and the object endpoint reads
  `set_permissions` fields from the top level, ignoring a nested
  `parameters`. Also recorded: eight document methods are legacy aliases of
  `/api/documents/<action>/`, and the object endpoint's `all`/`filters` widen
  the selection beyond the given ids. Source reads only; no live bulk edit
  was sent.
  Next review unchanged: 2027-03-18.

## 2026-09-26

- Added [GitHub and git behaviour behind integration branches](github-integration-branches.md),
  checked against GitHub.com documentation, the git 2.36 release notes and
  the knope 0.23.0 source. Covered up-to-date requirements, merge queue
  availability, workflow branch filters, closing keywords, retargeting,
  merge methods, knope's commit walk, `--remerge-diff` and `range-diff`.
  Single pass; the merge-queue availability claim was re-checked against the
  page. Draft until a first epic runs through it. Next review: 2027-03-26.

## 2026-09-25

- Recorded a departure in [MCP model-facing text](mcp-model-facing-text.md):
  Anthropic's "caveats or limitations" is read as limits that hold for
  every call by design, and failures that depend on one call's state stay
  out of descriptions for the error text. No claim changed. Next review unchanged: 2027-03-23.
- Revised [MCP tool outcomes and errors](mcp-tool-outcomes-and-errors.md)
  for fastmcp-pvl-core 10.0.0 by source and by re-running the in-memory
  probe on FastMCP 4.0.9. The request-logging middleware now logs
  `tool_call_failed` at a `ToolError`'s `log_level`, and a new claim
  records pvl-core's `tool_boundary`: one ERROR `tool_failed` record with
  the traceback and a fixed "the request itself was fine" message for any
  exception that is not a FastMCP error. The other table rows are unchanged
  from 9.0.1. Next review unchanged: 2027-03-25.
- Revised [MCP model-facing text](mcp-model-facing-text.md): markdown-vault-mcp
  removed `tests/test_client_surface_budget.py` and its aggregate ceilings
  (markdown-vault-mcp#1600, #1601). The 2026-09 baseline now cites the last
  commit that carried the test and the design text, and a new claim records
  that no source derives an aggregate ceiling; only the per-item client
  limits stay. Next review unchanged: 2027-03-23.
- Added [MCP tool outcomes and errors](mcp-tool-outcomes-and-errors.md),
  checked against the MCP 2026-07-28, 2025-11-25 and 2025-06-18 schema and
  tools pages at commit ab3a39c1, FastMCP 4.0.9, the MCP Python SDK 2.2.0 and
  fastmcp-pvl-core 9.0.1 source plus an in-memory probe, the Anthropic, OpenAI
  and Gemini tool-result docs, and the reference, GitHub, Sentry and Notion
  servers' source. Found that the spec never says whether "not found" or
  "permission denied" sets `isError`, that the Python SDK logs an anticipated
  `ToolError` at INFO while FastMCP defaults it to ERROR, and that pvl-core's
  middleware logs every raised `ToolError` as `tool_call_failed` at ERROR.
  Refute pass re-read the schema, the issue 199 ruling, the SDK and FastMCP
  docstrings, Anthropic's `is_error` wording and the Sentry and filesystem
  sources; host-side handling of `isError` stays unverified. Next review:
  2027-03-25.
- Added [Negative outcomes and faults outside MCP](negative-outcomes-and-faults.md),
  widening the same question beyond MCP: RFC 9110 and 9457, gRPC status codes,
  google.rpc.Code, AIP-193/194, the SRE Workbook, OpenTelemetry semconv v1.44.0
  (HTTP, gRPC, recording errors) and the Trace API, GraphQL September2025 with
  graphql.org, Apollo and Shopify, JSON-RPC 2.0, and the Rust, Go, Python,
  .NET, Java and Swift error-handling docs. Found broad agreement that a
  valid negative outcome is not a fault (OpenTelemetry leaves server-side 4xx
  and NOT_FOUND unset; only 5xx burns the SRE example SLO), and disagreement
  on which wire slot carries not-found. Refute pass re-read the OpenTelemetry,
  RFC 9110, gRPC, SRE, graphql.org, Rust and Python quotes. Next review:
  2027-09-25.

## 2026-09-23

- Added [MCP model-facing text](mcp-model-facing-text.md), checked against
  the MCP 2026-07-28 and 2025-11-25 schemas, the Claude, OpenAI, Gemini,
  VS Code and Cursor documentation, and FastMCP 4.0.5 by probe. Covered
  who reads each description field, Claude Code's 2,048-unit cut and
  tool-search deferral, FastMCP's docstring parsing (the issue 4952 leak
  and the unparsed resource docstring), pvl-core's instruction roles,
  the markdown-vault-mcp surface baseline, and SEP-2640 skills over MCP
  with FastMCP's skills provider probed on the wire. Refute pass re-fetched the
  claims the skill depends on; the Cursor tool cap and the Claude Desktop
  resource UI stay unverified. The same pass found the template scaffold's
  own `ping`, `status` and `summarize` docstrings shipping developer
  commentary and a framework link as their wire descriptions, and fixed
  them there. Next review: 2027-03-23.

## 2026-09-21

- Added [document field projection on lists and searches](paperless-document-fields-projection.md)
  for [#164](https://github.com/pvliesdonk/paperless-mcp/issues/164). Read
  Paperless 3.1.3 `DynamicFieldsModelSerializer` and `SearchResultSerializer`.
  Compared a full page with one projected to every field but `content`, on
  lists and searches at payload versions 9 and 10: every other key and value
  matched, and the payload fell from 2.2 MB to 101 KB (list) and from 10.5 MB to
  33 KB (search). Paperless 2.x was not read, and neither was the cost inside
  Paperless. Next review: 2027-03-21.

- Added [custom field updates on select fields](paperless-custom-field-select-patch.md)
  for [#171](https://github.com/pvliesdonk/paperless-mcp/issues/171). Read
  Paperless 3.1.3 `CustomFieldSerializer.validate`: the select branch runs on
  every update of a select field and demands `select_options`. Three live
  checks on throwaway fields, since deleted: the bare rename answered 400, a
  rename with the options resent answered 200 with them intact, and a
  name-only patch of a monetary field answered 200. Paperless 2.x was not
  read. Next review: 2027-03-21.

- Added [correspondent `last_correspondence` on list and detail](paperless-correspondent-last-correspondence.md)
  for [#172](https://github.com/pvliesdonk/paperless-mcp/issues/172). Read
  Paperless 3.1.3 `CorrespondentViewSet`: `retrieve` always annotates, `list`
  only on a non-empty `last_correspondence` query value. Three live checks:
  omitted, `true` and `false` behave as described, and ordering by the field
  without the parameter returned 500. Compared list and detail keys on five
  resources; only correspondents differed. Paperless 2.x was not read and the
  aggregate cost was not measured beyond a small instance. Next review:
  2027-03-21.

- Added [document permission keys on read and write](paperless-document-write-shape.md)
  for [#173](https://github.com/pvliesdonk/paperless-mcp/issues/173). Read
  Paperless 3.1.3 `DocumentSerializer` and `DocumentViewSet`: PATCH and PUT force
  `full_perms`, which swaps `user_can_change` and `is_shared_by_requester` for
  `permissions`. Confirmed the two GET shapes live; the PATCH shape rests on the
  source and on the issue reporter's call, not on a PATCH sent here. Paperless
  2.x was not read. Next review: 2027-03-21.

## 2026-09-20

- Rechecked the trigger-to-legacy-type mapping in Paperless 3.1.3
  `TaskSerializerV9` for the #161 review follow-up. Email and folder consumes
  explicitly map to `auto_task`; the mapping remains unchanged. Added the
  exact mapping and a test pin to [API payload versions](paperless-api-versioning.md).
  Tests cover every known trigger and the unknown-trigger fallback. A read-only
  live check returned a v10 task envelope and valid MCP resource JSON for 25
  tasks. No email-consume task was returned, so that mapping was not confirmed
  against a live record.

- Extended [API payload versions](paperless-api-versioning.md) for #139 after
  checking task serializers/models and both generations' filters. Task status
  query values are lowercase on 3.x; 2.x uses uppercase status and task_name.
  V10 saved-view visibility is absent rather than false. Fixtures and HTTP/MCP
  tests cover negotiation, pagination, compatibility projections and waiting;
  no fresh live instance capture was made.

- Added [Core tool registration composition](core-tool-registration.md) and
  extended [transfer links](core-transfer-links.md) for #158. Checked core
  7.2.0 registrars and execution boundaries; real-registrar tests refute the
  earlier claim that local metadata and errors preclude Jobs Path 1. Transfer
  validation receives no TTL, so receipt retention uses the configured maximum
  while core owns actual link expiry. Native client/Docket execution was not
  exercised.

## 2026-09-19

- Added [Core transfer links and Paperless text ingestion](core-transfer-links.md)
  for #111 and #112, checked against core 7.2.0 and Paperless 3.1.3 release
  sources. The refute pass found two material differences from informal
  descriptions: successful uploads are replayable during grace, and the
  download handler enforces no byte cap. Markdown acceptance follows detected
  MIME and installed parsers; frontmatter is not ingestion metadata. No live
  archive mutations were performed. Next review: 2027-03-19.

## 2026-09-18

- Added [GitHub repository security settings](github-repository-security-settings.md),
  checked against GitHub.com documentation and two read-only API probes.
  Covered the private-vulnerability-reporting, vulnerability-alerts and
  `security_and_analysis` endpoints, their visibility and licence limits, and
  the security policy file's locations. Single pass, no refute pass and no
  writes: the page is `draft` until a generated project's bootstrap run
  confirms the calls. Next review: 2027-03-18.

- Added [Paperless-NGX bulk edit and deferred search indexing](paperless-bulk-edit-indexing.md),
  read from paperless-ngx at the `v3.1.3` tag and from a live 3.1.3 instance.
  Written for [#141](https://github.com/pvliesdonk/paperless-mcp/issues/141),
  which asked whether `bulk_edit_documents` should say that its `OK` precedes
  the search-index rebuild.
- The pass settled both questions the issue left `[unverified]`. The other
  three `bulk_edit_*` tools are **not** affected: `BulkEditObjectsView.post`
  runs `set_permissions` and `delete` inline and queues nothing. And no
  handle on the queued task can identify it — `_extract_input_data` stores
  input only for `consume_file` and `mail_fetch`, so every `bulk_update`
  record carries `input_data: {}` and `related_document_ids: []`, at payload
  version 10 as much as at 9.
- A scratch-tag probe reproduced the symptom the issue could not: straight
  after the `OK`, a full-text search for the new tag returned nothing while
  the equivalent tag filter returned the document. That distinction — whoosh
  reads lag, ORM reads do not — is what the tool description now states.
- The refute pass narrowed one claim. "Bulk edits queue a reindex" is true
  only of the nine metadata methods; `delete`, `reprocess`, `rotate`,
  `split`, `delete_pages` and `merge` dispatch different tasks or none, so
  the page records the dispatch per method rather than for the endpoint.
  Next review: 2027-03-18.

## 2026-09-17

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
