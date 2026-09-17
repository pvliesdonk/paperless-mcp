---
type: Reference
title: Paperless-NGX API payload versions 9 and 10
description: How Paperless negotiates the Accept-header payload version, and every difference between version 9 and version 10 in the responses this client parses.
subject_version: "3.1.3 (d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e)"
valid_for: "paperless-ngx 3.x"
generated:
  by: process:researching-references
  at: 2026-09-17
stale_after: 2027-03-17
status: stable
verified:
  - by: process:researching-references
    at: 2026-09-17
sources:
  - id: pngx-settings
    title: paperless-ngx src/paperless/settings/__init__.py (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/paperless/settings/__init__.py
    accessed: 2026-09-17
  - id: pngx-middleware
    title: paperless-ngx src/paperless/middleware.py (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/paperless/middleware.py
    accessed: 2026-09-17
  - id: pngx-views
    title: paperless-ngx src/paperless/views.py (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/paperless/views.py
    accessed: 2026-09-17
  - id: pngx-doc-views
    title: paperless-ngx src/documents/views.py (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/views.py
    accessed: 2026-09-17
  - id: pngx-serialisers
    title: paperless-ngx src/documents/serialisers.py (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/serialisers.py
    accessed: 2026-09-17
  - id: pngx-api-md
    title: paperless-ngx docs/api.md, "API Versioning" (v3.1.3)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/docs/api.md
    accessed: 2026-09-17
  - id: pngx-2x-settings
    title: paperless-ngx src/paperless/settings.py (v2.20.15, the last 2.x release)
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v2.20.15/src/paperless/settings.py
    accessed: 2026-09-17
  - id: drf-versioning
    title: Django REST framework rest_framework/versioning.py (AcceptHeaderVersioning)
    resource: https://github.com/encode/django-rest-framework/blob/master/rest_framework/versioning.py
    accessed: 2026-09-17
---

# Paperless-NGX API payload versions 9 and 10

Paperless-NGX negotiates a payload version through the `Accept` header. This
client pins version 9; the instance it connects to defaults to version 10 and
accepts both. The two versions are not interchangeable: one endpoint this
client already parses changes shape completely between them, and the response
header that looks like it reports the negotiated version does not. This page
records which differences are real, so the pin is a decision rather than an
accident.

## Scope

- Covers: how the `Accept`-header version is negotiated and what an
  unacceptable version does; what the `X-Api-Version` and `X-Version`
  response headers actually report; and every payload difference between
  version 9 and version 10, both those this client would meet and those it
  would not.
- Does not cover: the routes Paperless 3.x exposes that this client does not
  call — that is `paperless-3x-rest-surface.md` — or Paperless 2.x payloads
  beyond which versions a 2.x instance accepts.
- Depended on by: `src/paperless_mcp/client/_http.py` (the `_ACCEPT_HEADER`
  pin), `src/paperless_mcp/client/tasks.py` (client-side task pagination),
  `src/paperless_mcp/models/task.py` (`Task`, `TaskStatus`), and
  `src/paperless_mcp/models/common.py` (`Paginated`).

## Claims

### Negotiation

- Paperless sets `DEFAULT_VERSIONING_CLASS` to DRF's
  `AcceptHeaderVersioning`, so the version travels as a media-type parameter
  on the `Accept` header (`application/json; version=N`) and never in the URL.
  [source: pngx-settings] [source: pngx-api-md]
  [pins: tests/unit/client/test_http.py::test_accept_header_pins_version]
- At 3.1.3, `ALLOWED_VERSIONS` is `["9", "10"]` and `DEFAULT_VERSION` is
  `"10"`, so a request that sends no version parameter is served version 10.
  [source: pngx-settings] [source: pngx-api-md]
- A version outside the accepted set is refused with **HTTP 406** and the body
  `{"detail":"Invalid version in \"Accept\" header."}`; the request is not
  served at any fallback version. DRF raises `NotAcceptable` before the view
  runs.
  [source: drf-versioning] [source: pngx-api-md]
  [observed: `GET /api/documents/?page_size=1` with `Accept: application/json; version=11` against 3.1.3 on 2026-09-17]
- A malformed or empty version parameter is refused the same way, so the
  failure is not limited to numbers above the allowed range and omitting the
  value is not equivalent to omitting the parameter.
  [observed: the same request with `version=banana` and with `version=`, each returning HTTP 406 with the identical body, on 2026-09-17]
- No per-view override of the versioning class exists. The only
  `versioning_class` in the tree is `src/documents/versioning.py`, which
  implements *document* versions (a `?version=<doc_id>` query parameter) and
  is unrelated to API payload versioning — a name collision worth not
  conflating.
  [observed: `versioning_class|version_param` grepped across `src/` at d48663e9, returning only that file]

### What the response headers report

- `X-Version` carries the Paperless version the instance runs (`3.1.3`), not a
  payload version. [source: pngx-middleware]
  [observed: response headers of `GET /api/documents/1/suggestions/` on 2026-09-17]
- **`X-Api-Version` does not report the version the response was rendered at.**
  The middleware sets it to the last entry of `ALLOWED_VERSIONS` — always
  `"10"` at 3.1.3 — regardless of what the caller negotiated, and only for
  authenticated requests. [source: pngx-middleware]
  [observed: `GET /api/documents/?page_size=1` at `version=9` returned `X-Api-Version: 10` while its body carried the version-9-only `all` key; the same request at `version=10` returned the same header with `all` absent, on 2026-09-17]
- A caller therefore cannot learn which payload version it received from the
  response; the only reliable signal is the version it asked for.
  [source: pngx-middleware]
- Neither header is present on a 406 refusal.
  [observed: the 406 responses above carried no `X-Api-Version` or `X-Version`, on 2026-09-17]

### Differences this client would meet

- Every **paginated list envelope** carries an extra `all` member at version 9
  that version 10 omits. `_should_include_all` returns true only for versions
  below 10, and appends `get_all_result_ids()` — the IDs of *every* matching
  object across all pages, not just the page returned.
  [source: pngx-views]
  [observed: `GET /api/documents/?page_size=1` at version 9 returned an `all` array of 244 entries beside `count: 244`, and no `all` at version 10, on 2026-09-17]
- Dropping `all` costs this client nothing: `Paginated` is declared
  `extra="ignore"` and has discarded that array since #25.
  [pins: tests/unit/models/test_common.py::test_paginated_drops_all_ids_from_upstream]
- **`/api/tasks/` changes shape entirely.** `TasksViewSet` selects
  `TaskSerializerV9` below version 10 and `TaskSerializerV10` otherwise, and
  suppresses pagination below version 10, so version 9 returns a **bare JSON
  array** and version 10 a `{count, next, previous, results}` envelope.
  [source: pngx-doc-views]
  [observed: `GET /api/tasks/` at both versions against 3.1.3 on 2026-09-17]
- Within a task, version 10 renames four members: `task_name` → `task_type`,
  `type` → `trigger_source`, `result` → `result_data`, and
  `related_document` (a single int or null) → `related_document_ids` (a list
  of ints). [source: pngx-serialisers]
  [observed: the first task object compared across both versions on 2026-09-17]
- Version 10 drops `task_file_name` and `duplicate_documents`, and adds
  `task_type_display`, `trigger_source_display`, `status_display`,
  `date_started`, `duration_seconds`, `wait_time_seconds` and `input_data`.
  [source: pngx-serialisers]
  [observed: the same comparison on 2026-09-17]
- **`status` changes case and vocabulary.** Version 9 serves the uppercase
  Celery strings (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`, `REVOKED`) via a
  compatibility map; version 10 serves the lowercase model values (`pending`,
  `started`, `success`, `failure`, `revoked`) plus a title-cased
  `status_display`. [source: pngx-serialisers]
  [observed: a task serving `"SUCCESS"` at version 9 and `"success"` with `status_display: "Success"` at version 10, on 2026-09-17]
- Version 9's `result` is not the raw result but a **reconstructed sentence**
  built from `result_data` (for example `"Success. New document id 42
  created"`); version 10 exposes the structured `result_data` object instead.
  A client reading `result` as prose is reading a version 9 artefact.
  [source: pngx-serialisers]
- The `?task_name=` and `?type=` query filters are honoured **only** at
  version 9, where they are mapped onto `task_type` and `trigger_source`;
  `?task_id=` works at both. At version 10 they are not rejected but
  **silently dropped** — the filter set exposes `task_type` and
  `trigger_source` under their new names, so django-filter discards the old
  spellings without a 400 and returns an unfiltered page.
  [source: pngx-doc-views]
- The document `created` field is byte-identical at both versions on 3.1.3.
  `docs/api.md` lists "created is now a date, not a datetime" under version 9,
  but no runtime branch implements it at this release, so both versions serve
  the same date-shaped value. [source: pngx-api-md] [source: pngx-doc-views]
  [observed: `GET /api/documents/1/` at both versions returned `created: "2018-11-01"` and byte-identical values for every other member, on 2026-09-17]
- Of the endpoints this client calls, **these two differences are the only
  ones**: the document detail, statistics, notes, history, metadata,
  suggestions, `remote_version` and `ui_settings` bodies, and the tag,
  correspondent, document-type and custom-field listings, compared equal
  apart from `all`.
  [observed: seventeen endpoints fetched once per version and compared as recursive key sets, with the document detail also compared value by value, against 3.1.3 on 2026-09-17]

### Differences this client would meet only once it holds the data

These were **not** observable on the connected instance, whose
`saved_views`, `share_links` and `storage_paths` collections are all empty, so
no item was compared. They are recorded from source, and a key-set comparison
against a populated instance would confirm them.

- **Saved views carry two extra booleans at version 9.**
  `SavedViewSerializer.to_representation` adds `show_on_dashboard` and
  `show_in_sidebar` below version 10, computed from the requesting user's
  `UiSettings`; version 10 omits both, and they are not in `Meta.fields`.
  [source: pngx-serialisers] [unverified] A saved view existing on the
  instance, fetched at both versions, would confirm it.
- **Writing a saved view silently drops those keys at version 10.** Below
  version 10 they are validated and persisted into the user's `UiSettings`;
  at version 10 the request falls through to stock DRF, which ignores the
  unknown keys without a 400. An upgrade therefore turns a persisted
  preference into a no-op rather than an error. [source: pngx-serialisers]
  [unverified] This client does not write saved views, so it is recorded as a
  hazard rather than a dependency.
- **The tag listing's `all` is wider than the envelope's.** When a listed tag
  has descendants, `/api/tags/` replaces `all` with the parent tags plus their
  descendant primary keys, below version 10 only. [source: pngx-doc-views]
- The legacy bulk-edit methods (`merge`, `rotate`, `edit_pdf`,
  `remove_password`, `split`, `delete_pages`, `delete`, `reprocess`) remain
  accepted on `/api/documents/bulk_edit/` at **both** versions; version 10
  moved them to dedicated endpoints but kept the old path working, logging a
  deprecation server-side. The version is interpolated into that log line
  only, so request and response are identical across versions.
  [source: pngx-doc-views] [source: pngx-serialisers]

### Which instances accept which version

- Version 10 arrived in **3.0.0** (published 2026-07-22), which simultaneously
  dropped every version below 9. The whole "Version 10" section of
  `docs/api.md` is present at 3.0.0 and unchanged through 3.1.3, so version 10
  semantics are a 3.0.0 event and not a 3.1.x one. [source: pngx-api-md]
- The last 2.x release, 2.20.15, ships `ALLOWED_VERSIONS = ["1" … "9"]` with
  `DEFAULT_VERSION = "9"`. A client pinning version 10 is therefore refused
  with a 406 by **every** 2.x instance, while version 9 is accepted by both
  2.x and 3.x. [source: pngx-2x-settings] [source: pngx-settings]
- Paperless commits to supporting an older API version "for at least one year
  after the release of a new API version", so version 9 has a documented
  horizon rather than an indefinite one. [source: pngx-api-md]
- Additive changes reach version 10 **without** a version bump: `SavedView.icon`,
  workflow action types 7 and 8, and the `/api/config/` remote-OCR fields all
  appeared across 3.1.x under the same version number. Pinning a version fixes
  the breaking changes, not the additive ones. [source: pngx-api-md]

### What version 10 would cost this client today

- Moving the pin to 10 breaks task handling in four independent ways:
  `TasksClient.list` iterates the response as a bare list and would iterate
  the envelope's *keys*, `TasksClient.get` guards on `isinstance(body, list)`
  and would return `None` for every lookup, `Task.status` is a closed
  `StrEnum` of uppercase values that a lowercase `success` fails, and
  `Task.result` / `Task.related_document` / `Task.type` name members version
  10 no longer sends.
  [observed: the version 10 task payload above read against `src/paperless_mcp/client/tasks.py` and `src/paperless_mcp/models/task.py` on 2026-09-17]
  [pins: tests/unit/client/test_tasks.py::test_list_all, tests/unit/models/test_task.py::test_task_status_values]
- No other parsed model depends on a member version 10 changes, because the
  only other difference this client meets is the ignored `all` array.
  [observed: the comparison above, on 2026-09-17]

## Where this project departs from the subject

- **The pin stays at version 9.** The instance defaults to 10 and this client
  asks for 9 deliberately: the only difference that reaches a parsed model is
  the task payload, version 9 is the shape every task model, fixture and test
  already encodes, and version 9 is the only value both 2.x and 3.x instances
  accept. Moving to 10 is a rework of `client/tasks.py`, `models/task.py` and
  their fixtures, tracked separately rather than smuggled into an unrelated
  change.
- The pin is asserted as a literal so the choice cannot drift silently.
  Before this page, `test_accept_header_pins_version` checked only that *some*
  `version=` was sent, so an edit from 9 to 10 would have passed the suite.
  [pins: tests/unit/client/test_http.py::test_accept_header_pins_version]

## Not covered

- The saved-view and tag-listing differences above were read from source but
  not reproduced, because the connected instance holds no saved views, share
  links or storage paths. [unverified] A populated instance, or a fixture
  built from one, would settle them.
- Whether any endpoint this client does **not** call differs between the two
  versions beyond those recorded here; the sweep covered the six
  version-branch sites in the source and the seventeen endpoints this client
  calls, not every route. [unverified]
- The search-semantics change is a 3.0.0 behaviour change rather than a
  version-10 one: `?query=` moved from Whoosh to Tantivy, and unqualified
  queries were explicitly not migrated. It is out of scope here and belongs
  with the search surface. [source: pngx-api-md]
