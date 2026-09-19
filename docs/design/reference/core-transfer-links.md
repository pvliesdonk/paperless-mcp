---
type: Reference
title: Core transfer links and Paperless text ingestion
description: Transfer sink contracts, HTTP retries, and Markdown upload acceptance.
subject_version: "fastmcp-pvl-core 7.2.0; Paperless-NGX 3.1.3"
valid_for: "fastmcp-pvl-core 7.x and Paperless-NGX 3.1.x"
generated:
  by: process:researching-references
  at: 2026-09-19
verified:
  - by: process:researching-references-refute
    at: 2026-09-19
stale_after: 2027-03-19
status: stable
sources:
  - id: register
    title: Core transfer registration and link minter
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_transfer/register.py
    accessed: 2026-09-19
  - id: sink
    title: Core transfer sink protocol and errors
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_transfer/sink.py
    accessed: 2026-09-19
  - id: routes
    title: Core transfer HTTP handlers
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_transfer/routes.py
    accessed: 2026-09-19
  - id: store
    title: Core transfer token state machine
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_transfer/store.py
    accessed: 2026-09-19
  - id: config
    title: Core transfer configuration
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_transfer/config.py
    accessed: 2026-09-19
  - id: upload
    title: Paperless document upload serializer
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/documents/serialisers.py
    accessed: 2026-09-19
  - id: kv
    title: Core namespaced KV factory
    resource: https://github.com/pvliesdonk/fastmcp-pvl-core/blob/v7.2.0/src/fastmcp_pvl_core/_kv_store.py
    accessed: 2026-09-19
  - id: text
    title: Paperless built-in text parser
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/paperless/parsers/text.py
    accessed: 2026-09-19
  - id: registry
    title: Paperless parser registry
    resource: https://github.com/paperless-ngx/paperless-ngx/blob/v3.1.3/src/paperless/parsers/registry.py
    accessed: 2026-09-19
---

# Core transfer links and Paperless text ingestion

This reference covers the external contracts needed by issues #111 and #112.
The source pass checked the installed core 7.2.0 package against its release
tag, then re-read the handlers to check the protocol docstrings.

## Registration and sink

- `build_transfer_links(mcp, server_config, transfer_config, sink=...)` mounts
  `/transfer/{token}` and returns `TransferLinks` without registering tools;
  the domain validates handles before calling `mint_download` or `mint_upload`.
  [source: register]
- Both mint methods accept an opaque string handle and optional `ttl_s`, and
  return `url` and `expires_in_s`; the base URL is required, trailing slashes
  are removed, and the route suffix is appended without the MCP endpoint path.
  [source: register]
- `TransferSink.read(handle)` returns `TransferReadResult(body, media_type,
  filename)`; `write(handle, body)` returns a mapping served as JSON. The sink
  receives neither the HTTP request nor the capability token, so upload
  metadata and domain operation identity must be carried by the handle or
  resolved through it. [source: sink] [source: routes]
- `add_transfer_workflow` accepts the domain upload/download tool names and
  adds server instructions whose visibility follows those tools.
  [source: register]

## HTTP and replay

- GET downloads and PUT or POST uploads; the route authenticates possession
  by claiming the token, without checking an Authorization header or MCP
  read-only policy. Domain write checks belong in the sink too. External proxy
  authentication can impose a separate access requirement. [source: routes]
- Unknown, expired, consumed and wrong-kind links return 404; a live concurrent
  claim returns 409. Unsupported handled methods, including HEAD, return 405.
  [source: routes]
- A successful request makes its token available again with expiry shortened
  to the lesser of remaining lifetime and the grace period; replay calls the
  sink again and does not extend the original grace deadline. These links are
  therefore not strict one-shot links. [source: store] [source: routes]
- Both upload and download use this grace behavior; the public minter has no
  per-kind hard-burn setting, and configuration rejects a zero grace period.
  Domain upload operations need replay protection if repeated writes would
  create repeated backend jobs. [source: config] [source: register]
- Failed reads/writes release the claim for retry. Named sink errors select
  403, 404, 410, 429, 502, 503 or 504; the base `TransferSinkError` accepts any
  400–599 status. Unexpected exceptions propagate after release and normally
  become an opaque 500. [source: sink] [source: routes]
- Claims use a lease and per-claim fence; the implementation's lock is an
  `asyncio.Lock` on each store object, so it supplies no cross-process atomic
  claim guarantee merely because the KV backend is shared. [source: store]

## Limits and data

- Defaults are 3,600 seconds lifetime, 86,400 maximum, 60 grace, 60 lease and
  104,857,600 upload bytes; all values must be positive and finite, with default
  lifetime no greater than maximum. Explicit lifetimes above maximum are
  clamped. [source: config] [source: register]
- Upload bodies are read in chunks under the cap, then materialized as bytes;
  an oversized body returns 413 and releases the token. The download handler
  has no byte-cap check, despite the sink protocol's general bounded-body
  prose, and materializes the full body. [source: routes] [source: sink]
- Downloads use attachment Content-Disposition with ASCII fallback and a
  percent-encoded UTF-8 filename; control characters and quote/backslash
  delimiters are removed before building the header. [source: routes]

## Receipt storage

- `build_kv_store(server_config, namespace=...)` returns an `AsyncKeyValue`
  wrapped with a collection prefix chosen by the domain, so receipts can use
  the same configured backend without sharing the core transfer namespace.
  [source: kv]
- Factory URL precedence is `kv_store_url`, legacy `event_store_url`, then
  `file:///data/state` where usable or an in-memory fallback. Explicit file
  configuration fails rather than falling back when unusable. [source: kv]
- Each memory factory call creates a new store, and memory state is lost on
  restart; separate receipt and token stores therefore need persistent backend
  configuration if their records must survive restarting the server.
  [source: kv]

## Markdown ingestion in Paperless

- `DocumentUploadSerializer.validate_document` detects MIME from bytes using
  `magic.from_buffer`, then checks parser support; a `.md` extension or supplied
  multipart Content-Type does not by itself select a Markdown parser.
  [source: upload]
- The built-in text parser accepts `text/plain`, `text/csv` and
  `application/csv`, reads text directly, extracts no structured metadata and
  creates no PDF archive. It does not list `text/markdown`. [source: text]
- The registry also discovers external parsers, and selects among parsers
  supporting the detected MIME type by score; acceptance can differ by
  installation. [source: registry]
- Ordinary Markdown detected as `text/plain` follows the text path above;
  preserving its bytes does not apply YAML frontmatter as Paperless metadata.
  Exact detection for arbitrary documents is not guaranteed. [source: upload]
  [source: text] [unverified] No live Markdown upload was performed; a live
  instance upload and completed task would verify a particular file.

## Project checks and boundaries

The domain integration pins registration and HTTP behavior, representation
selection, Markdown body preservation, retry acknowledgements and visibility
enforcement. [pins: tests/test_transfers.py::test_transfer_routes]
[pins: tests/test_transfers.py::test_download_variants]
[pins: tests/test_transfers.py::test_markdown_round_trip]
[pins: tests/test_transfers.py::test_upload_replay]
[pins: tests/test_transfers.py::test_visibility_rejects_existing_links]
The [design](../document-transfers.md) records receipt recovery and the
single-process deployment boundary.

This pass does not establish cross-process exactly-once backend ingestion,
proxy behavior, or an atomic transaction across the Paperless API and KV
storage. A crash after backend acceptance but before saving its acknowledgment
requires a domain recovery decision.
