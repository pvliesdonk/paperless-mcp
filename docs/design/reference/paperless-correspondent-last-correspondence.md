---
type: Reference
title: Paperless-NGX correspondent last_correspondence on list and detail
description: When /api/correspondents/ includes last_correspondence, what switches it on, and what ordering by it does without it.
subject_version: "3.1.3 (d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e)"
valid_for: "paperless-ngx 3.x"
generated:
  by: process:researching-references
  at: 2026-09-21
stale_after: 2027-03-21
status: stable
verified:
  - by: process:researching-references
    at: 2026-09-21
sources:
  - id: pngx-views
    title: paperless-ngx src/documents/views.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/views.py
    accessed: 2026-09-21
  - id: pngx-serialisers
    title: paperless-ngx src/documents/serialisers.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/serialisers.py
    accessed: 2026-09-21
---

# Paperless-NGX correspondent last_correspondence on list and detail

`last_correspondence` is a computed field, not a column. The detail endpoint
always computes it; the list endpoint computes it only when the request asks.
A client that does not ask gets rows without the key, and a model that
defaults the missing key to `null` then reports "no correspondence" for
correspondents that have documents. That is
[#172](https://github.com/pvliesdonk/paperless-mcp/issues/172).

## Scope

- Covers: `GET /api/correspondents/` and `GET /api/correspondents/{id}/`, the
  `last_correspondence` key, and ordering by it.
- Does not cover: other resources' list and detail keys beyond the comparison
  below, or how the value is filtered by document permissions.
- Depended on by: `CorrespondentsClient.list` in
  `src/paperless_mcp/client/correspondents.py`.

## Claims

- `CorrespondentSerializer` declares `last_correspondence` as a read-only
  `DateField`, so the key is serialized only when the queryset row carries the
  annotation. [source: pngx-serialisers]
- `CorrespondentViewSet.retrieve` always annotates it with
  `Max("documents__created")` restricted to documents the user may see.
  [source: pngx-views]
- `CorrespondentViewSet.list` annotates it only when
  `request.query_params.get("last_correspondence", None)` is truthy. The test
  is on a non-empty string, not on a boolean. [source: pngx-views]
- With no such parameter, none of 9 rows carried the key; with
  `last_correspondence=true` all did, `null` for correspondents without
  documents and a date otherwise. [observed: curl with `Accept: application/json; version=10` against a live 3.1.3 instance, 2026-09-21]
- `last_correspondence=false` switches the annotation on like `true`.
  [observed: same instance and date, both values returned identical rows with the key present]
- `ordering=last_correspondence` is a listed ordering field, and without the
  parameter it answered HTTP 500; with `ordering=-last_correspondence` and
  `last_correspondence=1` it answered 200. [source: pngx-views]
  [observed: same instance and date]
  The 500 is presumably Django refusing to order by an unannotated name.
  [unverified]
- The OpenAPI schema shipped with 3.1.3 lists no `last_correspondence` query
  parameter on `/api/correspondents/`, so the switch is not discoverable from
  the schema. [observed: parameter list of the `get` operation in `paperless-openapi-3.1.3.json.gz`, read 2026-09-21]
- Of correspondents, tags, document types, custom fields and documents,
  correspondents was the only resource whose list rows lacked a key that the
  detail response carried. Storage paths and saved views had no rows to compare.
  [observed: union of list-row keys against the detail keys of the first row, same instance and date]

## Where this project departs from the subject

`CorrespondentsClient.list` always sends `last_correspondence=true`, so list
rows carry the value the detail call returns and ordering by it works.
[pins: tests/unit/client/test_correspondents.py::test_list_asks_for_last_correspondence]

## Not covered

- Cost of the aggregate on a large instance. The live instance held 244
  documents and 9 correspondents, where eight timed requests each way overlapped
  (about 0.04 to 0.14 seconds). [unverified]
- Paperless 2.x. [unverified]
