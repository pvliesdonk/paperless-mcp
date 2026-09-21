---
type: Reference
title: Paperless-NGX custom field updates on select fields
description: Why a PATCH of a select custom field must carry extra_data.select_options, and which other field types have no such requirement.
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
---

# Paperless-NGX custom field updates on select fields

A partial update of a custom field is validated as if it were a full one for
`select` fields. A rename that names only `name` is refused, though the
options it does not mention are not in question. That is
[#171](https://github.com/pvliesdonk/paperless-mcp/issues/171).

## Scope

- Covers: `PATCH /api/custom_fields/{id}/` on `select` and `monetary` fields
  and what the serializer requires of `extra_data`.
- Does not cover: creation payloads (see the per-type table in
  `docs/tools/index.md`) or how document values reference option ids.
- Depended on by: `CustomFieldsClient.update` in
  `src/paperless_mcp/client/custom_fields.py`.

## Claims

- `CustomFieldSerializer.validate` takes the select branch when `data_type`
  in the request is `select` **or** the stored instance is a `select` field.
  [source: pngx-serialisers]
- In that branch it raises `{"error": "extra_data.select_options must be a
  valid list"}` unless the request carries `extra_data` with a non-empty
  `select_options` list whose every entry has a non-empty `label`. Nothing
  in the branch tests whether the update is partial, so a body without
  `extra_data` fails it. [source: pngx-serialisers]
- The same branch gives each option that has no `id` a random 16-character
  one, and leaves existing ids alone. [source: pngx-serialisers]
- A `PATCH` of `{"name": ...}` on a select field answered HTTP 400 with that
  message. [observed: PATCH sent with the project HTTP client to a select field created for the check on a live 3.1.3 instance, 2026-09-21; the field was deleted afterwards]
- Re-sending the field's own options, ids included, with the new name answered
  200 and the options came back unchanged.
  [observed: same instance and date, options compared before and after]
- The monetary check needs `data_type` in the request, so a name-only `PATCH`
  of a `monetary` field is not refused. [source: pngx-serialisers]
  [observed: name-only PATCH of a monetary field answered 200, same instance and date]

## Where this project departs from the subject

`CustomFieldsClient.update` reads the field first whenever the patch leaves
`extra_data` unset and, for a `select` field, adds the field's current
`extra_data` to the PATCH. A rename then applies and every option keeps its
id. The cost is one extra GET per such update, and another writer's change to
the options between the read and the write is overwritten.
[pins: tests/unit/client/test_custom_fields_write.py::test_update_select_field_resends_current_options]
[pins: tests/unit/client/test_custom_fields_write.py::test_update_with_extra_data_skips_the_read]

## Not covered

- Whether Paperless refuses partial updates of select fields on purpose or by
  oversight. The serializer carries no comment on it. [unverified]
- Paperless 2.x. [unverified]
