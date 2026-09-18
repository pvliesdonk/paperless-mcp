---
type: Reference
title: Paperless-NGX bulk edit and deferred search indexing
description: What the two bulk-edit endpoints do before they answer OK, which follow-up work they queue, and how a caller can observe it.
subject_version: "3.1.3 (d48663e9ebaadc4b413a6ca3bc88cb5fbc4e468e)"
valid_for: "paperless-ngx 3.x"
generated:
  by: process:researching-references
  at: 2026-09-18
stale_after: 2027-03-18
status: stable
verified:
  - by: process:researching-references
    at: 2026-09-18
sources:
  - id: pngx-bulk-edit
    title: paperless-ngx src/documents/bulk_edit.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/bulk_edit.py
    accessed: 2026-09-18
  - id: pngx-views
    title: paperless-ngx src/documents/views.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/views.py
    accessed: 2026-09-18
  - id: pngx-tasks
    title: paperless-ngx src/documents/tasks.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/tasks.py
    accessed: 2026-09-18
  - id: pngx-handlers
    title: paperless-ngx src/documents/signals/handlers.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/signals/handlers.py
    accessed: 2026-09-18
  - id: pngx-models
    title: paperless-ngx src/documents/models.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/models.py
    accessed: 2026-09-18
  - id: pngx-filters
    title: paperless-ngx src/documents/filters.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/filters.py
    accessed: 2026-09-18
  - id: pngx-apps
    title: paperless-ngx src/documents/apps.py
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/apps.py
    accessed: 2026-09-18
---

# Paperless-NGX bulk edit and deferred search indexing

A bulk edit answers `{"result": "OK"}` before the work it started has
finished. The field change is written inside the request; the search-index
rebuild it triggers is a Celery task that runs afterwards, so a full-text
search issued straight after the `OK` can miss the documents just edited.
This page records which endpoint defers what, how long the deferred work
takes, and what a caller can observe — the questions
[#141](https://github.com/pvliesdonk/paperless-mcp/issues/141) asked.

## Scope

- Covers: what `POST /api/documents/bulk_edit/` and
  `POST /api/bulk_edit_objects/` do synchronously, which task each method
  queues, what that task does, whether it is observable through
  `/api/tasks/`, and which read paths are affected by the delay.
- Does not cover: Paperless 2.x, the LLM index's own timing (a separate
  `llm_index` task), whoosh's internal commit behaviour below the task
  boundary, or the bulk endpoints' permission model.
- Depended on by: `src/paperless_mcp/tools/documents.py`
  (`bulk_edit_documents`), `src/paperless_mcp/client/tasks.py`
  (`TasksClient.list`), `src/paperless_mcp/models/task.py` (`TaskType`),
  and `docs/design/long-running-calls.md` § "Only one of the three
  candidates blocks".

## Claims

### What the document bulk-edit endpoint does before it answers

- `BulkEditView.post` resolves the named method, calls it inline, and returns
  `Response({"result": result})`; the methods this client can reach all
  return the literal `"OK"`. [source: pngx-views] [source: pngx-bulk-edit]
- Nine methods dispatch `bulk_update_documents.apply_async(...)` after
  applying their change and before returning: `set_correspondent`,
  `set_storage_path`, `set_document_type`, `add_tag`, `remove_tag`,
  `modify_tags`, `modify_custom_fields`, `set_permissions` and
  `merge_as_versions`. [source: pngx-bulk-edit]
- The remaining methods queue something else or nothing. `delete` queues no
  reindex and is itself tracked as the task `documents.bulk_edit.delete`;
  `reprocess` dispatches `update_document_content_maybe_archive_file` per
  document; `rotate`, `split`, `delete_pages`, `edit_pdf`, `remove_password`
  and `merge` dispatch `consume_file` or a consume task for the documents
  they produce. A claim about `bulk_update` therefore does not generalise to
  every operation in the enum. [source: pngx-bulk-edit]

### The object bulk-edit endpoint queues nothing

- `BulkEditObjectsView.post` handles only `set_permissions` and `delete`, both
  entirely inline — owner and permission writes through the queryset, or
  `objs.delete()` — and then returns `Response({"result": "OK"})` with no
  `apply_async` call anywhere in the method. [source: pngx-views]
- This is the endpoint behind `bulk_edit_tags`, `bulk_edit_correspondents`
  and `bulk_edit_document_types`, so those three tools have no deferred
  indexing to declare. [source: pngx-views]

### What the queued task does

- `bulk_update_documents` clears each document's caches, re-sends
  `document_updated` and `post_save`, adds or updates every document in the
  search backend through one `batch_update()`, and — only when
  `AIConfig().llm_index_enabled` — updates the LLM index for the same ids.
  [source: pngx-tasks]

### Observing the queued task

- `documents.tasks.bulk_update_documents` is in `TRACKED_TASKS`, and
  `before_task_publish_handler` creates the `PaperlessTask` row with status
  `PENDING` when the task is published to the broker, so the record exists in
  `/api/tasks/` by the time the bulk edit's response arrives.
  [source: pngx-handlers] [observed: probe below, where the record was
  already present and `started` on the first poll after the `OK`]
- The record carries no link to the edited documents: `_extract_input_data`
  stores `{}` for every task type other than `consume_file` and `mail_fetch`,
  and the observed records report `input_data: {}` and
  `related_document_ids: []`. A caller can therefore only correlate by
  recency, not by document id — at either payload version.
  [source: pngx-handlers] [observed: 15 `bulk_update` records read from a live
  3.1.3 instance at payload version 10 on 2026-09-18]
- `PaperlessTaskFilterSet` exposes `task_type` as a `MultipleChoiceFilter`
  over `PaperlessTask.TaskType`, and the filter is honoured at payload
  version 9 as well as 10: `?task_type=bulk_update` returned the same 15
  records under both `Accept` headers. [source: pngx-filters]
  [observed: live 3.1.3 instance, 2026-09-18]
  [pins: tests/unit/client/test_tasks.py::test_list_tasks_task_type_filter_is_sent]
- `TasksViewSet` sets `ordering = ["-date_created"]`, so the most recently
  created task comes first — at payload version 9 too, where the response is
  an unpaginated list rather than an envelope. Recency is therefore readable
  off the head of the list, which is what makes correlation-by-recency usable
  at all. [source: pngx-views]
- `PaperlessTask.TaskType` has thirteen values: `consume_file`,
  `train_classifier`, `sanity_check`, `index_optimize`, `mail_fetch`,
  `llm_index`, `empty_trash`, `check_workflows`, `bulk_update`,
  `reprocess_document`, `build_share_link`, `bulk_delete` and
  `apply_ai_suggestions`. [source: pngx-models]
  [pins: tests/unit/tools/test_tasks.py::test_list_tasks_exposes_task_type_choices]

### Which reads actually lag

- Only the full-text index is deferred. `?query=` and `?more_like_id=` are
  served from the search backend, while tag, correspondent and type filters
  and single-document reads are ORM queries that see the committed change at
  once. [source: pngx-views] [observed: probe below]
- A single-document `PATCH /api/documents/{id}/` calls
  `get_backend().add_or_update(refreshed_doc)` inside the request, so
  `update_document` has no such lag — the asymmetry is between bulk and
  single edits, not between writing and reading. [source: pngx-views]
- `document_updated` is connected to workflow, websocket and LLM-index
  handlers only; the whoosh update is not on that signal, which is why it has
  to be called explicitly by the view or by the queued task.
  [source: pngx-apps]

### How long the window is

- Across 15 `bulk_update` records on the deployed instance (window
  2026-08-27 to 2026-09-17, payload version 10, so
  `wait_time_seconds + duration_seconds` is separable): median total 49.3s,
  95th percentile 420.8s, maximum 434.4s. [observed: `/api/tasks/` history;
  the same sample is tabulated in `docs/design/long-running-calls.md`]
- A one-document probe on 2026-09-18 bounds the other end: the bulk edit
  returned `OK` after 0.11s, a full-text search for the new tag returned 0
  hits at +0.16s while the equivalent tag filter returned 1, the document
  became searchable at roughly +0.4s, and the `bulk_update` task reached
  `success` at +4.7s. The window is real but scales with the selection and
  the queue, not with any fixed delay. [observed: scratch tag created, added
  to one document via `add_tag`, then removed and the tag deleted]

## Where this project departs from the subject

Nowhere. This server relays the upstream response unchanged; what
[#141](https://github.com/pvliesdonk/paperless-mcp/issues/141) changed is
what `bulk_edit_documents` promises and whether `list_tasks` can filter for
the queued task.

## Not covered

- Whether whoosh adds commit latency beyond the task's own duration.
  `[unverified]` The probe cannot separate them: the document became
  searchable before the task reached a terminal state, which suggests the
  batch commits per document rather than at the end, but nothing here
  establishes that.
- Whether the LLM index lags further behind on an AI-enabled instance. The
  bulk path calls `update_llm_index` once after the search backend update,
  and `llm_index` tasks on this instance run for ~1,200s, but no probe tied
  an AI-backed read to a bulk edit. `[unverified]`
- The behaviour of `all: true` / `filters` bulk-edit selections, which this
  client does not send. `[unverified]`
