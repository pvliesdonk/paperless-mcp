# Reference research log

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
