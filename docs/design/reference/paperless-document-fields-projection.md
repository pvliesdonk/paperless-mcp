---
type: Reference
title: Paperless-NGX document field projection on lists and searches
description: How the fields query parameter narrows a document response, what it cannot do, and what this client sends to keep OCR text out of list and search requests.
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

# Paperless-NGX document field projection on lists and searches

Paperless returns a document's full OCR text on every list and search row
unless the request names the fields it wants. A client that drops the text
after parsing still pays for downloading, parsing and holding it, which grows
with page size and document length.
[#164](https://github.com/pvliesdonk/paperless-mcp/issues/164) is that cost.

## Scope

- Covers: the `fields` query parameter on `GET /api/documents/` for plain
  lists and for searches, what it removes, what it leaves alone, and its size
  effect on one instance.
- Does not cover: `fields` on other endpoints, nested fields such as
  `notes[].note`, or the database and index cost inside Paperless.
- Depended on by: `_LISTING_FIELDS` and `_projection` in
  `src/paperless_mcp/client/documents.py`.

## Claims

- `DocumentViewSet.get_serializer` splits the `fields` query value on commas
  and hands it to the serializer. [source: pngx-views]
- `DynamicFieldsModelSerializer.__init__` drops every serializer field not
  named. A name that matches no field is ignored, so the parameter is a keep
  list only: there is no way to ask for "everything but `content`".
  [source: pngx-serialisers]
- A search request is served by `SearchResultSerializer`, which shares
  `DocumentSerializer.Meta` and so takes the same projection. It adds
  `__search_hit__` after building the row, so the hit data is not affected by
  the projection. [source: pngx-views] [source: pngx-serialisers]
- `truncate_content=true` exists and cuts `content` to 550 characters, which
  still sends text and changes the value where omitting it would not. It is not
  used. [source: pngx-serialisers]
- The `Document` response schema shipped with 3.1.3 lists the same fields as
  `_LISTING_FIELDS` bar `content`, and `_LISTING_FIELDS` adds only two
  write-only names, `set_permissions` and `remove_inbox_tags`.
  [pins: tests/unit/client/test_documents_list_search.py::test_listing_fields_are_the_3_1_3_document_schema_minus_content]
- Naming those fields left every other key and value of every row unchanged,
  on lists and on searches, at payload versions 9 and 10, and left the envelope
  keys and the row order unchanged.
  [observed: the same page fetched with and without a `fields` list naming all fields but `content`, rows compared key by key, 25 list rows and 12 search hits, against a live 3.1.3 instance, 2026-09-21]
- The effect on that instance, at version 10: a list page of 25 documents fell
  from 2,215,697 to 101,385 bytes, and a search page of 12 hits from 10,486,197
  to 32,919 bytes. Version 9 gave the same sizes within about a kilobyte.
  [observed: same requests, response body length in bytes]
- Request time fell as well, from about 0.19 to 0.15 seconds for the list and
  from about 0.84 to 0.58 seconds for the search, one request each.
  [observed: same requests, one timing each, so indicative only]

## Where this project departs from the subject

`DocumentsClient.list` and `search` send `fields` naming every field but
`content` unless `include_content` is true, when they send no projection. The
list is a constant rather than the fields of the `Document` model, because the
model declares fewer fields than Paperless returns and passes the rest through as
extras; projecting by the model would drop `mime_type`, `versions` and others
from list rows while `get_document` kept them.
[pins: tests/unit/client/test_documents_list_search.py::test_content_is_left_out_of_the_request_by_default]

The parse-time strip of `content` stays as a backstop for a server that ignores
the parameter. Nested `notes[].note` and `custom_fields[].value` are still
stripped after parsing, since a projection cannot reach inside them.

## Not covered

- A field Paperless adds after 3.1.3 is missing from list and search rows until
  it is added to `_LISTING_FIELDS`, while `get_document` returns it. Nothing
  catches that mechanically; the pin above checks the constant against the
  3.1.3 schema and moves only when that schema file is refreshed, and this page's
  `stale_after` date is the prompt to do so. [unverified]
- Paperless 2.x. Whether it honours `fields` on lists and searches was not
  read. [unverified]
- What Paperless itself saves: it still reads the text from its database and, for
  searches, builds the row from it. Only the transfer, parsing and memory on this
  side were measured. [unverified]
