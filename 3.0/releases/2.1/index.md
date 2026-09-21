# 2.1

This release makes the server describe itself accurately to the model it serves. Every tool now carries a human-readable title, the generated instructions name the Paperless instance the server fronts, and `bulk_edit_documents` states that the search-index rebuild it triggers runs after the call returns. `get_document_content` caps its text at 50,000 characters by default and can page through the rest, so a book-length document no longer arrives whole in a single tool result. That cap is the only changed default: see [Upgrading](#upgrading) if something you run depends on the full text.

## A long document no longer arrives whole

`get_document_content` returns at most 50,000 characters by default. A capped result opens with a marker naming the character range returned, the document's full length, and the `offset` to pass to read on from there; text that fits under the cap is returned unchanged, with no marker.

The tool had no cap at all before, which is what [#35](https://github.com/pvliesdonk/paperless-mcp/issues/35) reported: "`get_document_content(document_id)` returns the full OCR text with no cap. For a book-length document (hundreds of pages) this floods the LLM's context in a single tool call."

The size measurement behind the number comes from one deployed archive of 244 documents. The median document there holds 88,080 characters, and the largest (a 1,009-page specification) holds 2,407,894. At 50,000 characters, 36.5% of that archive is returned complete. Paging ships in the same release rather than later, because for the other 63.5% the `offset` is the only route to the text past the cap. What generalises from that archive is the shape of the distribution rather than its median, since an archive of receipts and letters would rarely reach any cap.

Two ways to read past the cap:

- `max_chars=None` returns the entire text however long it is.
- `offset=<value from the marker>` continues from where the previous call stopped.

`max_chars` must be greater than zero and `offset` cannot be negative, so a caller cannot construct a call that returns nothing and asks to continue.

Two paths deliberately stay uncapped. The `paperless://documents/{document_id}/content` resource takes no arguments, so there is nowhere to pass a cap, and it still returns the full text. `get_document(include_content=True)` is also still uncapped, tracked as [#149](https://github.com/pvliesdonk/paperless-mcp/issues/149). [Tools](https://pvliesdonk.github.io/paperless-mcp/3.0/tools/index.md) and [Resources](https://pvliesdonk.github.io/paperless-mcp/3.0/resources/index.md) document both.

## Every tool carries a title

Each registered tool now has an `annotations.title`: a human-readable label that clients supporting titles display in place of the machine name. The tables in [Tools](https://pvliesdonk.github.io/paperless-mcp/3.0/tools/index.md) still list machine names, which is what you pass when calling a tool.

Most titles restate the name in prose. A few say what the tool does instead: `get_remote_version` is titled **Check for Paperless Updates**, and `get_document_metadata` is titled **Get Document File Details**. No tool was renamed, and no title replaces a name a caller uses.

[#107](https://github.com/pvliesdonk/paperless-mcp/issues/107) filed the gap as structural debt: "No registered tool carries an `annotations.title`, so title-aware MCP clients label all 49 of them with their raw machine names." Its argument for fixing the whole surface at once was that a title is per-tool, so "every new tool lands untitled too, and the gap grows with the tool surface." An enforcement test now fails the build when a tool arrives without one.

Titles need no configuration. They are attached when the tools register, so they are part of every `tools/list` response; a client that ignores titles keeps showing machine names.

## The instructions name the instance

The generated instructions now state which Paperless the server is connected to, and how a link to it maps onto the document tools. With `https://paperless.example.org` configured, the text reads: "This server fronts the Paperless-NGX instance at https://paperless.example.org. A link of the form https://paperless.example.org/documents/<id>/ names a document by its id; pass that id to the document tools."

[#114](https://github.com/pvliesdonk/paperless-mcp/issues/114) asked for this because the server knew the URL and never said it: "A model given a link such as `https://paperless.example.org/documents/42/` in conversation has no stated basis for recognising it as this server's instance, or for mapping it to `get_document(42)`." What the release adds is that stated basis. How much a given model uses it is not measured here.

The URL comes from `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL`, or from `PAPERLESS_MCP_PAPERLESS_URL` when the public variable is unset. That is the same value the `web_url` and `share_url` fields in tool results are built from, so the instructions and those links always name one host. Both variables already existed; nothing new is required to configure.

The instructions deliberately say nothing about the `paperless://` resource URIs. The issue asked for those too, and its author withdrew that half before any of it shipped, on the grounds that `resources/read` is "a client-to-server request" ([correction on #114](https://github.com/pvliesdonk/paperless-mcp/issues/114#issuecomment-5718846776)): a model cannot fetch a resource on its own initiative, and almost every resource has a tool twin it can call instead. Naming the URI family would have described an action the model cannot take. [Configuration](https://pvliesdonk.github.io/paperless-mcp/3.0/configuration/index.md) covers the instruction variables.

## A bulk edit says that indexing is deferred

`bulk_edit_documents` now states what happens after it answers `OK`. Paperless writes the field change inside the request and then queues the search-index rebuild as a background task, so `search_documents` can miss the edited documents for seconds to minutes, while `list_documents` and `get_document` reflect the change at once. Single-document edits through `update_document` are unaffected: that path updates the search index inside the request.

[#141](https://github.com/pvliesdonk/paperless-mcp/issues/141) reported the silence rather than the delay: "`bulk_edit_documents` answers `{"result": "OK"}` while the work its call queued is still running, and nothing in the response says so." On the instance measured there, 15 of those queued rebuilds ran to a median of 49.3 seconds, and to 420.8 seconds at the ninety-fifth percentile. That is long enough for a model to search and find nothing.

`list_tasks` gained a `task_type` filter so the queued work can be found: `list_tasks(task_type="bulk_update")` returns the rebuild tasks, newest first, and `wait_for_task` waits for one to finish. Records carry no link back to the documents an individual edit touched, so the most recent task is the available handle rather than an exact match.

The `bulk_edit_tags`, `bulk_edit_correspondents` and `bulk_edit_document_types` tools are unchanged, because the endpoint behind them applies its work inline and queues nothing. [Tools](https://pvliesdonk.github.io/paperless-mcp/3.0/tools/index.md) documents both descriptions.

## Upgrading

Nothing in this release requires an operator to change configuration. No environment variable changed, and no deployment layout changed.

One default behaviour changed: `get_document_content` used to return a document's whole text and now stops at 50,000 characters. Anything that depended on receiving the full text in one call should pass `max_chars=None`, or follow the `offset` the truncation marker names. Automation that reads short documents sees no difference, since text under the cap is returned unchanged and carries no marker.

The tool surface grew: titles on every tool, `max_chars` and `offset` on `get_document_content`, and `task_type` on `list_tasks`. MCP clients discover this on connect, so a client holding a cached tool list needs a reconnect to see it. For Python consumers, `TaskType` is a new export from `paperless_mcp.models`; nothing was removed or renamed.
