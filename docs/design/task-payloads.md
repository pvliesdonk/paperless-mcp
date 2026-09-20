# Task payload versions

Issue #139 moves the default Accept header to payload version 10. Paperless
2.x remains supported: an explicit DRF `406` with the invalid Accept-version
message retries the request at version 9 and caches that choice for the client
session. The response's `X-Api-Version` is not used as a negotiated-version
signal. Other errors do not downgrade. Rejection occurs before the versioned
view runs, so the retry also applies to writes; ordinary transient write
failures still are not retried. The version retry does not consume the
transient-error retry budget. Restart after upgrading a connected 2.x server
to negotiate again.

`client/_payload.py` isolates the fallback condition and query differences.
The HTTP layer selects the version for each attempt, so even a first task call
that falls back sends the right filters: lowercase status and task_type at
v10, uppercase status and task_name at v9, including the two legacy type-name
aliases. The v9 request omits page parameters because its response is a full
array. `TasksClient` parses v10 page envelopes without slicing them again and
slices v9 arrays locally. UUID lookup accepts both list shapes; waiting uses
the same lookup and terminal-status set.

The task model retains uppercase `TaskStatus` values and existing library
fields. It also accepts lowercase input and exposes v10 task/trigger labels,
start time, durations, input_data, result_data and every related document ID.
Legacy projections follow Paperless's own v9 serializer: result prose is
reconstructed from structured results, type groups trigger sources, and
related_document is the first ID. The complete v10 values remain intact.
Version 9 data is never reverse-parsed into invented structured results or
precise trigger sources. Existing arbitrary upstream fields remain allowed.

Saved views are the deliberate library compatibility break. V10 removes
show_on_dashboard and show_in_sidebar; both now default to None instead of
False so unavailable preferences cannot look disabled. Callers using the
Python models must accept nullable booleans. V9-provided values remain intact.
This earns the breaking marker even though 2.x connectivity and the task
library interface are retained.

The [external reference](reference/paperless-api-versioning.md) records the
source behavior and pins the relevant tests. The v10 fixture is constructed
from the 3.1.3 serializer/model fields, not claimed as a fresh live capture.
No live upstream documents or tasks are changed by validation.
