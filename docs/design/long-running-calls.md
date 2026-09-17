# Calls that outlast a client's patience

Internal design note. Not published; not Vale-linted.

Answers the research issue
[#110](https://github.com/pvliesdonk/paperless-mcp/issues/110) (appetite: one
day). The question it was given: does any call this server makes block long
enough to need the pvl-core Jobs framework, and what does wiring that framework
actually cost?

The issue expected the answer to be "not needed yet", in the owner's words "not
sure there is anything (yet)". The measurement says otherwise, for one tool, and
for a reason the issue did not anticipate.

## Verdict

**Warranted, for `wait_for_task` only.** On the deployed instance a document
consume triggered over the REST API — the path a `wait_for_task` caller waits
on — takes a median of **46.8 seconds** and a 95th percentile of **113.7
seconds**, against a `wait_for_task` default timeout of 60 seconds. Twenty of
the 44 observed uploads (45%) ran longer than that default and would have
failed on the tool's own deadline rather than on anything wrong with Paperless.

The counterfactual is worth stating plainly, because it is the load-bearing
inference here: these 44 consumes are historical uploads, not calls anyone
actually waited on through this tool. What is measured is how long Paperless
took; what is inferred is that a caller waiting on the same work would have
timed out. The inference is safe because `wait_for_task` polls until the task
reaches a terminal status, so the task's own duration is exactly what it waits
for.

**But the sample is one batch, and that changes what the verdict means.** All 44
uploads landed on a single day, in three bursts, with a median inter-arrival gap
of **1.2 seconds**. Inside a burst the wait climbs monotonically — 0.0s, 13.9s,
31.5s, and on up to 112.9s — while execution never exceeds 8.1s for any of the
44. Each burst's *first* upload waited essentially nothing (0.0s, 0.0s, 0.1s).

So the queue those uploads waited in was **their own**. Paperless consumes with
a single worker by default, so 37 documents arriving roughly a second apart and
taking ~2s each to process necessarily back up, and the nth upload waits about
2n seconds. The 359s outlier fits the same shape: it arrived five minutes after
the burst and still waited 358.2s behind the backlog, on 1.2s of work.

The honest verdict is therefore narrower than "consumes are slow":

- **A single ad-hoc upload does not need a job.** It completes in two to four
  seconds and comes nowhere near the 25s soft deadline, let alone the 60s
  default.
- **Batch ingestion does, and reliably.** Past roughly the thirteenth document
  in a burst, every subsequent `wait_for_task` exceeds 25s, and past the
  thirtieth it exceeds 60s. Nothing about that is pathological or
  misconfigured; it is what one worker and a queue do.

That distinction matters for sequencing rather than for the answer, because
batch ingestion is the normal shape of agent-driven upload, and
[#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) will make it
more common by removing the context-window ceiling that currently discourages
a many-document upload. It is the issue that carries an upload path
(`create_upload_link`); its sibling
[#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) is the download
side — OCR content out as a file — and so does not change how many consumes
are queued. An earlier version of this note named both, which was wrong.

The other two candidates the issue named are **not** long-running calls at all,
because neither waits for the work it starts. That was worth measuring: it
removes two thirds of the issue's scope.

The integration cost is low and was paid end-to-end in a spike (below). Nothing
blocks adopting it; this note does not itself adopt it.

## Method

Read from the task history of the deployed instance rather than by uploading
test documents. `/api/tasks/?include_acknowledged=true` returns every historical
task, so the distribution was already there to be read, and no document was
created, mutated or deleted to obtain it.

Deliberately not measured through this MCP server's own `upload_document`: that
path takes file bytes as a base64 tool argument, which is the shape
[#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) and
[#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) exist to replace.
Timing it would have measured a transport that is on its way out. The numbers
below are Paperless's own consume latency, independent of how the bytes arrive.

- **Sample**: 4,133 task records, window 2026-08-27 to 2026-09-17. The 44
  API-upload consumes that carry the verdict all fall on 2026-09-16, in three
  bursts; see the batch finding below, which is the main caveat on these
  numbers.
- **Instance**: Paperless-NGX 3.1.3 (`settings.version` of `/api/ui_settings/`),
  AI features enabled.
- **Read at both payload versions.** Version 9, which this client pins, carries
  only `date_created` and `date_done`, so a duration derived from it conflates
  queue wait with execution. Version 10 adds `date_started`,
  `duration_seconds` and `wait_time_seconds`, which separates them. Both were
  fetched; the split below comes from version 10. Those fields are already
  recorded in `reference/paperless-api-versioning.md`.

Reproducible with:

```python
# GET /api/tasks/?include_acknowledged=true with
#   Accept: application/json; version=10
# then, per record, wait_time_seconds + duration_seconds is what a caller waits.
```

## What the numbers say

Total wall-clock is `wait_time_seconds + duration_seconds`: what a caller
waiting on the task actually experiences.

| Task | Trigger | n | p50 wait | p50 exec | p50 total | p95 total | max |
|---|---|---|---|---|---|---|---|
| `consume_file` | `api_upload` | 44 | 45.7s | 1.7s | 46.8s | 113.7s | 359.4s |
| `consume_file` | `web_ui` | 7 | 7.9s | 1.6s | 10.0s | 91.3s | 91.3s |
| `consume_file` | `folder_consume` | 5 | 9.9s | 3.4s | 13.2s | 23.2s | 23.2s |
| `bulk_update` | `system` | 15 | 3.7s | 26.0s | 49.3s | 420.8s | 434.4s |
| `llm_index` | `manual` | 3 | 0.1s | 1214.6s | 1214.6s | 1401.9s | 1401.9s |
| `mail_fetch` | `scheduled` | 3007 | 0.05s | 0.09s | 0.14s | 0.21s | 478.7s |

`api_upload` is the row that matters: it is exactly the trigger source Paperless
records for an upload over the REST API, which is what this server does.
Confirmed rather than assumed, by joining the same records across both payload
versions: version 9's legacy `type` field maps one-to-one onto version 10's
`trigger_source` (`manual_task` covers `api_upload`, `web_ui` and `manual`;
`auto_task` covers `system` and `folder_consume`).

**The wait is queue wait, not work.** Median execution for a consumed document
is 1.7 seconds; median total is 46.8. The caller is not waiting for OCR, it is
waiting for a worker to pick the task up behind whatever else is queued. Three
consequences:

1. The delay is a property of how many consumes are queued ahead of this one —
   very often the caller's own batch — and not of the document. It cannot be
   predicted from file size or page count, and a "how long should this take"
   heuristic in the tool layer would be measuring the wrong variable.
2. It cannot be fixed by tuning `timeout_seconds`. Raising the default trades a
   failed call for a longer block, and the queue grows with the batch, so no
   fixed value is right for both the first document and the fortieth.
3. It is unusually well suited to promotion: the work is mostly idle waiting, so
   a promoted job costs nearly nothing to keep alive.

Against the three thresholds in play:

| Threshold | Value | `consume_file` / `api_upload` over it |
|---|---|---|
| `JobsConfig.soft_deadline_s` default | 25s | 33 of 44 (75%) |
| `wait_for_task` default `timeout_seconds` | 60s | 20 of 44 (45%) |
| MCP client request timeout | 180s | 1 of 44 (2%) |

The 180s figure is the one recorded in pvliesdonk/markdown-vault-mcp#937, the
failure that motivated ADR 0002. Note where the failure actually falls: almost
everything finishes inside the client's patience, but nearly half falls outside
`wait_for_task`'s own default. **The tool's deadline is the binding constraint,
not the client's.** The issue predicted exactly this ("fails at the deadline and
the model has to call again"); what it got wrong was assuming nothing was slow
enough to reach it.

## Only one of the three candidates blocks

| Candidate | Blocks? | Evidence |
|---|---|---|
| `wait_for_task` | **Yes** | Polls `/api/tasks/` every second up to `timeout_seconds` (default 60, ceiling 600) and raises `TimeoutError` at the deadline. |
| `upload_document` | No | Paperless's `PostDocumentView.post` returns `Response(async_task.id)` immediately after queueing (v3.1.3 `views.py:3390`). The tool returns a task id and waits for nothing. |
| `bulk_edit_documents` | No | `BulkEditView.post` runs the synchronous `.update()` inline and then `bulk_update_documents.apply_async(...)`, returning before the index rebuild runs. |

So the `bulk_update` row above, with its 421s p95, is real but invisible to the
caller: it happens after the HTTP response. That is worth its own issue rather
than a job — the tool answers `{"result": "OK"}` while the documents it edited
are not yet searchable, and nothing tells the model when they will be. A job
handle would be the wrong fix, because Paperless does not give the bulk-edit
response the task id it would need.

`llm_index` at 1400s is the slowest thing on the instance, but it is only
reachable through `/api/tasks/run/`, which this server does not wrap.

## What the integration costs

Paid in full on the `research/110-jobs-framework-spike` branch (commit
`fd31a77`), which is pushed for reference and **deliberately not proposed for
merge**. Every local gate passes on it: ruff, ruff format, mypy, 546 tests,
`gen_config_surface.py --check`, and the structural diff gate at 100% quality
with zero violations.

| Cost | Detail |
|---|---|
| Hand-written code | 76 lines across 7 files (config, domain, `_context`, `tools/__init__`, `tools/tasks`, the docs table, and the one test below) |
| Generated files | 107 lines across 7 files, all from one `gen_config_surface.py` run |
| New operator surface | 3 env vars: `PAPERLESS_MCP_JOBS_SOFT_DEADLINE_S`, `_RESULT_TTL_S`, `_MAX_PER_SUBJECT` |
| New tool | `get_job_result`, pvl-core-owned shape, registered once |
| Tests changed | 1 |

Six things the spike learned that reading the API would not have told us:

- **Promotion alone does not remove the tool's own deadline.** As wired, the
  coroutine handed to `run_with_deadline` is still
  `client.tasks.wait_for(timeout_seconds=...)` with its 60s default, so a 100s
  consume is promoted at 25s and then the *job* fails at 60s with the same
  `TimeoutError` — off-screen instead of inline. The functional check showed
  exactly this: with `timeout_seconds=3` the job ended `failed` carrying "did
  not complete within 3.0s". Adoption therefore also means changing the inner
  wait — no deadline once promoted, or the 600s ceiling as the default — or the
  handle just relocates the failure it was meant to prevent.

- **The config generator does see a nested dataclass.** `jobs: JobsConfig` in
  the `CONFIG-FIELDS` block raised the collected variable count from 45 to 48,
  even though `JobsConfig.from_env(_ENV_PREFIX)` is not the literal
  `env(prefix, "SUFFIX")` call the AST scan looks for. scholar-mcp's claim to
  the same effect holds here. All seven generated files go stale until
  regenerated, which is a mechanical step, not a judgement call.
- **Path 1 is unusable here.** `register_long_running_tool` registers the tool
  itself through `mcp.tool`, which bypasses this repo's `register_tool` and
  therefore loses the icon registry, the annotation registry, and the
  Paperless-error-to-`ToolError` wrapper. Path 2 (`build_jobs` plus
  `run_with_deadline`) composes cleanly and keeps all three. Any future
  long-running tool here should assume path 2.
- **The typed output schema is the one unavoidable loss.** `wait_for_task` has
  to widen from `Task` to `dict[str, Any]`, because the caller now receives
  either the task or a handle.
- **Wiring the poller changes the server's instructions.** `register_job_tools`
  calls `instructions_for(mcp).add(...)` itself, inserting a paragraph about
  job handles. That broke an exact-match assertion in `test_smoke.py`, which is
  the test doing its job: the cost is not confined to the tool count.
- **Job records are lost on restart under the default store.**
  `build_kv_store` defaults to `file://` at `/data/state` where that directory
  is usable and `memory://` otherwise. On a host without `/data`, a promoted
  job's result does not survive a restart. Anything adopting this should set
  `PAPERLESS_MCP_KV_STORE_URL` deliberately.

One more, about scoping: with `auth=none`, which is how this server runs today,
`get_subject()` returns nothing and every caller shares the anonymous job scope.
`max_per_subject` is therefore effectively a global cap, and job ids are not
isolated between callers. That is acceptable for a single-operator deployment
and would not be for a shared one.

The spike was verified working, not merely compiling: with
`PAPERLESS_MCP_JOBS_SOFT_DEADLINE_S=0.05`, `wait_for_task` returned a handle,
and `get_job_result` polled it through to `failed` carrying the underlying
`TimeoutError`. Promotion, the record store, the env wiring and the poller all
work together.

Adopting this is **not a breaking change**, per the two-part test in
`AGENTS.md`: it touches neither the operator surface in a way that requires
action (the three new variables all have defaults) nor the public library
interface, and on the MCP surface the previous behaviour stays reachable — a
consume that finishes inside the soft deadline still answers inline.

## When to revisit

The verdict above is for `wait_for_task`. Two already-filed issues will bring
calls that exceed the 25s soft deadline by design rather than by queue
contention, and they are the natural first consumers of this machinery:

- [#137](https://github.com/pvliesdonk/paperless-mcp/issues/137) — the chat
  endpoint, which streams an LLM response.
- [#138](https://github.com/pvliesdonk/paperless-mcp/issues/138) — the AI
  suggestions endpoint, whose documented failure mode is a 503 on timeout.

If either is implemented, wire jobs then if not before. Recording this here is
the point: a later "is it needed yet" question should start from these numbers
rather than re-derive them.

## Not established

- Whether anything *other than* a caller's own batch makes a consume wait.
  Every long wait observed is explained by burst self-queuing, so ambient load
  from the scheduled tasks is not evidenced either way. `[unverified]` The
  instance's `mail_fetch` runs often (3,007 of 4,133 records) but at a p95 of
  0.21s, which is far too short to accumulate the waits seen here; it was
  initially suspected as the cause and the arrival-gap data refuted that.
- What Paperless's consume concurrency actually is on this instance. The
  single-worker reading is inferred from the monotonic wait climb and the
  upstream default, not read from the deployment. `[unverified]` A larger
  `PAPERLESS_TASK_WORKERS` would flatten the curve without changing its shape.
- Whether a second, independent batch reproduces the ~2s-per-document slope.
  `[unverified]` Only one day's uploads exist in the window.
- The `mail_fetch` maximum of 478s against a p95 of 0.21s is unexplained.
  `[unverified]` Not investigated; it is a scheduled task no tool waits on.
