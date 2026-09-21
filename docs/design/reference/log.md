# Reference research log

## 2026-09-21

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
