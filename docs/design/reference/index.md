---
okf_version: "0.2"
---

# External behavior references

These pages record external behavior, with source markers and review dates.
Read the relevant page before relying on its claims; research it again when
its `stale_after` date passes. Project decisions belong in `docs/design/`.

- [GitHub planning objects](github-planning-objects.md) — milestones,
  issue relationships, and PR design material used by roadmapping and releases.
- [Core tool registration composition](core-tool-registration.md) — metadata,
  icon helpers and Jobs error boundaries.
- [Core transfer links and Paperless text ingestion](core-transfer-links.md) —
  sink contracts, retry grace, HTTP limits, and Markdown upload acceptance.
- [Paperless-NGX version endpoints](paperless-version-endpoints.md) — which of
  `/api/remote_version/`, `/api/ui_settings/` and `/api/status/` reports the
  installed version, which reports the newest release, and what each costs in
  permissions.
- [Paperless-NGX API payload versions 9 and 10](paperless-api-versioning.md) —
  how the `Accept`-header version is negotiated, what the `X-Api-Version`
  header really reports, and every payload difference between the two
  versions, including the reshaped `/api/tasks/`.
- [Paperless-NGX bulk edit and deferred search indexing](paperless-bulk-edit-indexing.md)
  — what the two bulk-edit endpoints do before answering `OK`, which follow-up
  task each queues, how long the search-index rebuild takes, and what a caller
  can observe through `/api/tasks/`.
- [The Paperless-NGX 3.x REST surface this server does not expose](paperless-3x-rest-surface.md)
  — the 93-route inventory against the 30 this client wraps, and how the
  Paperless AI chat and suggestion endpoints behave.

See the [research log](log.md) for completed research passes. Add project
references here as they are written.
