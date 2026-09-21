---
type: Reference
title: Paperless-NGX document permission keys on read and write
description: Which of user_can_change, is_shared_by_requester and permissions a document body carries on GET versus PATCH and PUT, and why.
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
  - id: pngx-serialisers
    title: paperless-ngx src/documents/serialisers.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/serialisers.py
    accessed: 2026-09-21
  - id: pngx-views
    title: paperless-ngx src/documents/views.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e/src/documents/views.py
    accessed: 2026-09-21
---

# Paperless-NGX document permission keys on read and write

A document body carries one of two mutually exclusive sets of permission keys,
and Paperless picks the set by request method, not by anything the caller asks
for. A client that returns the PATCH body next to a GET body hands out two
shapes for the same document. That is [#173](https://github.com/pvliesdonk/paperless-mcp/issues/173).

## Scope

- Covers: the permission-related keys of a document body on `GET`, `GET
  ?full_perms=true`, `PATCH` and `PUT` of `/api/documents/{id}/`, and how
  Paperless decides between them.
- Does not cover: the contents of `permissions` beyond its `view`/`change`
  outline, `set_permissions` bulk edits, or other object types.
- Depended on by: `DocumentsClient.update` in
  `src/paperless_mcp/client/documents.py`.

## Claims

- `OwnedObjectSerializer.__init__` removes `user_can_change` and
  `is_shared_by_requester` when `full_perms` is set, and removes
  `permissions` when it is not. A body therefore carries the first two keys or
  the third, never both. [source: pngx-serialisers]
- `DocumentViewSet.get_serializer` reads `full_perms` from the query string,
  default false, and passes it with `kwargs.setdefault`. [source: pngx-views]
- `DocumentSerializer.__init__` then overwrites `kwargs["full_perms"]` with
  `True` whenever the request method is `PATCH` or `PUT`, under the comment
  "return full permissions if we're doing a PATCH or PUT". The query-string
  value cannot switch this off. [source: pngx-serialisers]
- A plain `GET` of a document returned `user_can_change`,
  `is_shared_by_requester` and `owner` and no `permissions`; `GET
  ?full_perms=true` returned `owner` and `permissions` only.
  [observed: curl with `Accept: application/json; version=10` against document 448 on a live 3.1.3 instance, 2026-09-21]
- A `PATCH` body carries `permissions` and lacks `is_shared_by_requester`.
  [observed: reported in #173 from an `update_document` call on a 3.1.3 instance, 2026-09-21; not reproduced with a direct PATCH here]
  This follows from the two serializer claims above.
- The forcing lives in `DocumentSerializer` only; the other owned objects
  (tags, correspondents, document types, storage paths) use the base
  `OwnedObjectSerializer` without it. [source: pngx-serialisers]

## Where this project departs from the subject

`DocumentsClient.update` discards the PATCH body and re-reads the document with
a plain `GET`, so `update_document` returns the same shape as `get_document`.
The cost is one extra request per update.
[pins: tests/unit/client/test_documents_write.py::test_update_returns_the_shape_get_returns]

## Not covered

- Paperless 2.x. The `full_perms` forcing on PATCH and PUT was read at 3.1.3
  only. [unverified]
- Whether the read after the write can ever miss the write. Paperless updates
  the row inside the request, so none was expected, but no concurrent-writer
  case was tried. [unverified]
