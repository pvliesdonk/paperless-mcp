# Tool outcomes

Internal design note. Not published; not Vale-linted.

Every tool ends in one of the four outcomes of the `designing-tool-outcomes`
skill: a result, a request the model must change, a stale read it must refresh,
or a server fault. The evidence is in
`reference/mcp-tool-outcomes-and-errors.md` and
`reference/negative-outcomes-and-faults.md`; this page records how this server
maps Paperless onto them.

## The boundary

Every tool is `@mcp.tool` → `@tool_boundary` → `@paperless_errors` → body.
`paperless_errors` (`src/paperless_mcp/tools/_errors.py`) turns every
Paperless failure into a `ToolError` with the level below; `tool_boundary`
catches anything else as a server fault (one `tool_failed` record at ERROR, a
fixed "the request was fine" message). `tests/test_tool_outcomes.py` fails a
tool registered without the boundary.

## Paperless answers

The level answers "who has to act":

| Paperless answered | Outcome | Level | Why |
|---|---|---|---|
| 400 | change the request | INFO | Paperless's `detail` names the field; the model resends |
| 403 | change the request | INFO | Paperless's per-object policy for the token's user, a valid "no" rather than a fault; the model tells the user |
| 404 on a call with id arguments | change the request | INFO | a wrong id; the model looks it up |
| 404 on a call without one | fault | ERROR | no id to be wrong: the route is missing, so the URL or the instance is |
| other 4xx | change the request | INFO | same as 400 |
| 409 | refresh, then retry | INFO | the object changed underneath |
| 429, 5xx, status 0 (no answer), `httpx.RequestError` | fault that heals itself | WARNING | nobody acts; the model retries later |
| 401 | fault | ERROR | the server's own token is broken: configuration |
| a response the models reject (pydantic) | fault | ERROR | Paperless changed shape or the models are wrong: a bug |

403 and 401 share `AuthError` in the client; the classifier splits them on
`status_code`, because only 401 needs an operator. The 403 reading matches the
`ui_settings` precedent in `AGENTS.md`, where a narrower service account is an
expected deployment, not a failure.

For the INFO rows the middleware's `tool_call_failed` line is the only log
record. For WARNING and ERROR, `paperless_errors` also logs Paperless's own
detail (`tool_api_error`, `tool_validation_error`, `tool_network_error`)
because the message to the model leaves it out. The model-actionable rows log
no `tool_api_error`.

## What a message carries

- A 404 quotes the call's id arguments by name and value (`document_id=42`)
  and names the tool that looks each one up; `paperless_errors` binds them
  from the call, capped so a long `ids` list stays short. The transfer hook
  names the id as `ref.document_id`, the part of the ref the model passed.
- Paperless's `detail` goes in only for 400, 409 and other 4xx, where it names
  what the model sent wrong. It is collapsed to one line, capped at 240
  characters, dropped when it is an HTML page, and always ends a sentence.

## Outcomes raised in tool bodies

- `wait_for_task` reaching its deadline is INFO: the model can wait again or
  read the task with `get_task`. The return type stays `Task`. The poll ends
  the same way for an id Paperless never knew, so one more read tells the two
  apart and the message names the case; a task that finished since the last
  poll is returned.
- `upload_document` with content that is not base64 is INFO. Decoding uses
  `validate=True`, so stray characters are refused instead of silently dropped.
- The transfer `validate` hook reports a malformed `ref` as INFO, naming the
  part pydantic rejected, and refuses `variant: "archive"` for a document with
  no archived PDF when the link is minted, where the model sees it. Only the
  ref is parsed under that INFO rule; a reply from Paperless that fails
  validation reaches the tool boundary as a server fault.

## Descriptions

Descriptions state the contract only; how a call fails lives in the error text
above (the `writing-model-facing-text` skill). Parameters shared by several
tools carry their descriptions once, in `tools/_params.py` (paging, ordering,
name filters, bulk arguments) and `models/_fields.py` (matching rules).

The facts in the descriptions are sourced, not recalled: the query syntax
`search_documents` teaches is the "Searching" section of Paperless 3.1.3's
`docs/usage.md`; ordering fields, filters, bulk methods and their parameters
come from 3.1.3's views, serialisers and the vendored OpenAPI document in
`reference/`.
