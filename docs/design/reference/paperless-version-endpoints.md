---
type: Reference
title: Paperless-NGX version endpoints
description: What /api/remote_version/, /api/ui_settings/ and /api/status/ each report about "the Paperless version", and what each costs in permissions.
subject_version: "3.1.3 (ae9529551d17395c69dedf63a4472b45df0dab0f)"
valid_for: "paperless-ngx 3.x"
generated:
  by: process:researching-references
  at: 2026-09-16
stale_after: 2027-03-16
status: stable
verified:
  - by: process:researching-references
    at: 2026-09-16
sources:
  - id: pngx-views
    title: paperless-ngx src/documents/views.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/ae9529551d17395c69dedf63a4472b45df0dab0f/src/documents/views.py
    accessed: 2026-09-16
  - id: pngx-perms
    title: paperless-ngx src/documents/permissions.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/ae9529551d17395c69dedf63a4472b45df0dab0f/src/documents/permissions.py
    accessed: 2026-09-16
  - id: pngx-settings
    title: paperless-ngx src/paperless/settings/__init__.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/ae9529551d17395c69dedf63a4472b45df0dab0f/src/paperless/settings/__init__.py
    accessed: 2026-09-16
  - id: pngx-urls
    title: paperless-ngx src/paperless/urls.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/ae9529551d17395c69dedf63a4472b45df0dab0f/src/paperless/urls.py
    accessed: 2026-09-16
  - id: pngx-serialisers
    title: paperless-ngx src/documents/serialisers.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/ae9529551d17395c69dedf63a4472b45df0dab0f/src/documents/serialisers.py
    accessed: 2026-09-16
  - id: drf-permissions
    title: Django REST framework — Permissions
    resource: https://www.django-rest-framework.org/api-guide/permissions/
    accessed: 2026-09-16
---

# Paperless-NGX version endpoints

Three Paperless endpoints answer something that reads like "the Paperless
version", and they do not answer the same question. One reports the newest
release published on GitHub; two report the version the instance is actually
running, at different permission costs. Conflating the first with the other two
is the defect this page exists to stop recurring: it is invisible on a fully
up-to-date instance and wrong exactly when an update is pending.

## Scope

- Covers: what each of `/api/remote_version/`, `/api/ui_settings/` and
  `/api/status/` returns for the version, where each value comes from inside
  Paperless, and what permission each call requires.
- Does not cover: the rest of the `ui_settings` or `status` payloads, the
  update-check UI, API payload version 9 vs 10 differences (that is
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113)), or
  Paperless 2.x handlers.
- Depended on by: `src/paperless_mcp/client/system.py`
  (`remote_version`, `installed_version`),
  `src/paperless_mcp/models/system.py` (`RemoteVersion`, `UiSettingsResponse`),
  `src/paperless_mcp/domain.py` (`upstream_version_provider`), and the
  `get_server_info` wiring in `src/paperless_mcp/server.py`.

## Claims

### `/api/remote_version/` — the newest release published upstream

- The response body has exactly two keys, `version` and `update_available`.
  [source: pngx-views] [pins: tests/unit/models/test_system.py::test_remote_version_roundtrip]
- `version` is the `tag_name` of the latest release read from
  `api.github.com/repos/paperless-ngx/paperless-ngx/releases/latest`, with a
  legacy `ngx-` prefix stripped — not a value the instance knows about itself.
  [source: pngx-views] [pins: tests/unit/client/test_system.py::test_remote_version]
- The instance's own running version is parsed only to compute
  `update_available` and is never returned by this endpoint. [source: pngx-views]
- When the GitHub fetch fails, `version` is the literal `"0.0.0"` and nothing is
  cached, so a caller cannot distinguish "no update" from "could not check"
  without reading `update_available` alongside it. [source: pngx-views]
- A successful lookup is cached server-side for 15 minutes under the
  `remote_version_view_latest_release` cache key. [source: pngx-views]
- The view declares no `permission_classes`, and the project sets no
  `DEFAULT_PERMISSION_CLASSES` in its `REST_FRAMEWORK` block
  [source: pngx-settings]; Django REST framework documents that when the
  setting is unspecified it "defaults to allowing unrestricted access",
  `AllowAny` [source: drf-permissions]. So this endpoint costs no object
  permission, which is the one advantage it has over the two below.
- The route is registered unconditionally; the `PAPERLESS_ENABLE_UPDATE_CHECK`
  setting is surfaced to the web UI as `update_checking.backend_setting` and
  does not gate this endpoint. [source: pngx-urls] [source: pngx-settings]

### `/api/ui_settings/` — the version installed on the instance

- `GET` returns an envelope whose `settings` member carries `version`, set from
  Paperless's own `version.__full_version_str__` — the version the instance is
  running. [source: pngx-views]
  [pins: tests/unit/client/test_system.py::test_installed_version]
- The view's `permission_classes` are `IsAuthenticated` **and**
  `PaperlessObjectPermissions`. [source: pngx-views]
- `PaperlessObjectPermissions.perms_map` maps `GET` to
  `%(app_label)s.view_%(model_name)s`, which for this view's `UiSettings`
  queryset is `documents.view_uisettings`; a token whose user lacks it gets
  `403`. [source: pngx-perms]
  [pins: tests/unit/client/test_system.py::test_installed_version_needs_the_ui_settings_view_permission]
- The serializer's `settings` field is `DictField(required=False)`, so a
  bodyless `GET` validates and no request body is needed.
  [source: pngx-serialisers]
  [pins: tests/unit/client/test_system.py::test_installed_version_only_reads]
- The same path accepts a `POST` that writes the calling user's UI settings
  row, so a client reading the version must stay on `GET`.
  [source: pngx-views]
  [pins: tests/unit/client/test_system.py::test_installed_version_only_reads]

### `/api/status/` — the installed version, gated more strictly

- The response carries `pngx_version`, also set from
  `version.__full_version_str__`, so it answers the same identity question as
  `ui_settings`. [source: pngx-views]
- Its `permission_classes` are only `IsAuthenticated`, but the handler then
  calls `has_system_status_permission` and returns `403` when that is false.
  [source: pngx-views]
- `has_system_status_permission` requires the user to be a superuser, be staff,
  or hold `paperless.view_system_monitoring` — strictly more than the
  `ui_settings` route costs, which is why this server does not use it.
  [source: pngx-perms]

## Where this project departs from the subject

Nowhere in behaviour, but deliberately in *which* endpoint answers *which*
question:

- `get_server_info` reports identity and therefore reads `/api/ui_settings/`,
  never `/api/remote_version/`. Reading the latter as identity is the defect
  fixed in [#121](https://github.com/pvliesdonk/paperless-mcp/issues/121) and
  locked out by a test asserting the remote-version route goes uncalled.
  [pins: tests/test_smoke.py::test_get_server_info_tool_registered]
- The `get_remote_version` tool and the `remote-version://paperless` resource
  keep the upstream endpoint's own question — "is there a newer release" — and
  say so in their descriptions rather than in their names, which mirror
  Paperless's route. See the AGENTS.md "Key Design Decisions" entry.
- `/api/status/` is not called at all, because it costs more permission than
  `/api/ui_settings/` for the same answer.

## Not covered

- Paperless 2.x handlers were not re-read at this pass. The fixtures in
  `tests/fixtures/paperless/` are 2.x-shaped (`2.7.2`, `2.14.7`) and still
  validate against the models, which suggests the response shapes are
  unchanged, but that is inference about shape and not a check of 2.x
  behaviour. [unverified] Re-reading `RemoteVersionView` and `UiSettingsView`
  on the 2.x branch would settle it.
- Which Paperless version the deployed instance runs, and therefore which of
  these claims it exercises. [unverified]
- Whether API payload version 10 changes any of these three bodies: it does
  not. `/api/remote_version/` and `/api/ui_settings/` were compared at both
  versions and returned identical key sets, so the claims above hold either
  way. `ALLOWED_VERSIONS` is `["9", "10"]` with `DEFAULT_VERSION` `"10"` at
  this commit [source: pngx-settings], and this client still pins `version=9`;
  the differences that decide that pin live elsewhere in the surface and are
  recorded in
  [Paperless-NGX API payload versions 9 and 10](paperless-api-versioning.md),
  researched under
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113).
