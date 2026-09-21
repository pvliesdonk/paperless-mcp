# Document transfers

Issues #111 and #112 share one Paperless transfer sink. The HTTP deployment
registers `create_download_link` and `create_upload_link`
when `PAPERLESS_MCP_BASE_URL` is set. Existing inline tools and resources remain
available for metadata and bounded OCR reads, including under stdio and HTTP
without a public base URL. Whole originals, archived files and previews use the
HTTP transfer route instead of inline resources.

## Wiring decision

Path 1, `register_transfer_routes`, owns both generic tools, their metadata,
workflow instructions, HTTP route and token machinery. Paperless supplies a
sink, a validation hook and appended descriptions. A download `ref` is a JSON
string with `document_id` and optional `variant` (default `original`). An upload
`ref` has `filename` and optional `metadata`. Pydantic validates these domain
values before the hook returns an opaque handle; callers cannot supply upload
operation IDs or receipt deadlines. Paperless errors are translated inside
that hook independently of registration.

This replaces #155's domain tools under #158. Their typed parameters were a
local API choice, not a user requirement that core's generic tools could not
meet. Both kinds of reference retain the same file operations and explicit
metadata. The tools introduced by #155 had not shipped in a release, so their
names and allow/deny entries change together before release. The
[external reference](reference/core-transfer-links.md) records the core contract.

`TransferConfig` is composed into `ProjectConfig` and populated with its own
`from_env` reader. The generator discovers the composition, including all five
transfer variables. `server.py` wires the tools inside `DOMAIN-WIRING`, using
the same staged Paperless context as the existing tools.

The optional base-URL gate is deliberate: requiring it on every HTTP startup
would break existing deployments to add a capability they had not configured.
The public base URL addresses the server root, not the MCP endpoint or the
Paperless instance. Core mounts `/transfer/{token}` at the HTTP app root.

## Downloads and Markdown

The download tool checks document access before minting. Redemption fetches the
document again with the configured Paperless service account, so deleted
objects and revoked permissions fail then too. `original` retrieves the
original bytes; `archive` requires an archived filename and never silently
substitutes the original; `preview` uses Paperless's preview endpoint.

`content` returns all OCR text, unchanged, after a YAML front-matter block with
ID, title, created timestamp, correspondent ID, document type ID and tag IDs.
JSON encoding each value keeps quotes, newlines, nulls and lists valid in YAML
without letting a title inject fields. Related-object names would add API
requests and a second set of access failures, so the export uses IDs. No OCR
layout or Markdown structure is invented.

Inline reads have a 20,000-character maximum, and offset paging remains
available.
Structured tool and resource responses omit OCR content, and document lists and
searches leave it out of the Paperless request too (see
[the fields projection reference](reference/paperless-document-fields-projection.md)).
The content resource returns the same bounded preview, while full files and OCR
Markdown use this transfer route. Downloads fetch current data at redemption rather than pinning
a snapshot at mint time. Core and the existing Paperless client materialize
file bytes in server memory; these links avoid model-context costs, not
server-memory costs. No archive file-size measurement was made as part of this
implementation.

## Uploads and retry receipts

The upload handle contains a unique operation ID, validated plain filename and
explicit metadata. The HTTP body is passed to the existing Paperless upload
client unchanged, including `.md` files. Paperless performs MIME detection and
consumption. Front matter is file content, not an instruction to change tags,
correspondents or titles. The HTTP acknowledgement contains `task_id`; callers
use `get_task` to check ingestion. Transfer completion means the file was
submitted, not that OCR or indexing finished. This keeps queue waiting out of
the transfer lease and needs no Jobs subsystem.

Core permits replay within a short grace window after success. `UploadReceiver`
persists a SHA-256 digest and a pending receipt before calling Paperless, then
stores the returned task acknowledgement. An identical replay returns that
acknowledgement without another POST. Different bytes, an in-progress request,
or a pending receipt left by a failed or interrupted POST return 409.

A crash between Paperless accepting the file and saving the receipt cannot be
made atomic across the two systems. The pending record intentionally survives:
inspect Paperless tasks before minting another link. This also applies to a
rejected upload whose receipt is still pending. The first failure retains its
mapped HTTP status, and the next attempt returns 409. Receipt storage failure
before submission cannot send bytes to Paperless.

Receipts use `build_kv_store` with namespace `paperless-upload-receipts`; they
contain no document bytes. Core's validator receives only the reference and
kind, not the requested TTL. The upload handle therefore records a conservative
retention deadline of creation time plus the configured maximum link lifetime;
receipt retention adds the Paperless request timeout. Core alone clamps the
actual link TTL. Keeping the retention deadline in the handle prevents a
shorter configuration after restart from expiring a pending receipt before its
original link. Persisted records survive a server restart when the
operator uses a persistent KV backend. Both core's claim lock and the receipt
lock are process-local: one server process must own a given transfer store.
Sharing it between concurrent replicas does not provide exactly-once uploads.

The sink enforces the current allow/deny list at redemption as well as minting,
so restricting a restarted deployment also blocks previously issued links for
the hidden tool. Possession of a URL otherwise grants access without MCP auth;
reverse proxies must route `/transfer/` for the receiving client.

## Verification

`tests/test_transfers.py` exercises MCP minting and HTTP redemption, including
all representations, Markdown body and metadata preservation, upload replay
across a reconstructed sink, concurrent retries, failed POST outcomes, caps,
invalid arguments, deployment gating and access revocation. The full registry
metadata test runs with transfer tools enabled. No live Paperless document was
created or changed during implementation.
