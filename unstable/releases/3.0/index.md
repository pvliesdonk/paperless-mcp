# 3.0

Compared with v2.1.0, this release keeps large OCR and binary files out of ordinary MCP responses. It prefers Paperless payload v10 with a v9 fallback, and task resources now emit valid timestamp JSON. HTTP and SSE deployments can move full files and OCR Markdown through expiring transfer links. The shared runtime moves to fastmcp-server-template v9 and fastmcp-pvl-core v9, which requires logging-variable changes and a review of explicit authentication settings.

## Transfer links for files and Markdown

HTTP and SSE deployments can move document files and full OCR text through expiring capability links instead of putting them into an MCP response. Set `PAPERLESS_MCP_BASE_URL` to the public server root and route `/transfer/` at the reverse proxy. The server then registers the generic `create_download_link(ref, ttl_s)` and `create_upload_link(ref, ttl_s)` tools. Download references select an original, archive, preview, or OCR Markdown variant. Upload references carry a filename and optional Paperless metadata; the response contains a Paperless task ID for `get_task`.

The links came from the need to handle scanned PDFs and long OCR text without placing whole files in model context ([#111](https://github.com/pvliesdonk/paperless-mcp/issues/111), [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112)). A persistent `PAPERLESS_MCP_KV_STORE_URL` keeps upload receipts across restarts. The transfer design documents replay handling, access checks at redemption, the upload limit, and the requirement to route `/transfer/` ([document transfer design](https://pvliesdonk.github.io/paperless-mcp/unstable/design/document-transfers/index.md)).

The final tool names and schemas come from pvl-core's registrar. The earlier domain-specific names were replaced before this release by the core Path 1 registrar ([#155](https://github.com/pvliesdonk/paperless-mcp/pull/155), [#159](https://github.com/pvliesdonk/paperless-mcp/pull/159)); those intermediate names were never in a stable release.

## Bounded document content

Inline OCR content has one 20,000-character limit across the MCP document surface. `get_document_content` and `paperless://documents/{id}/content` accept an offset so callers can page through longer text. The response identifies the returned range, total length, and next offset. Structured document tools no longer include OCR content, and the JSON document resource returns `content: null`.

Original and preview binary resources are no longer sent inline. Use the transfer links above for full files when the server runs over HTTP or SSE. Stdio deployments, and HTTP deployments without `PAPERLESS_MCP_BASE_URL`, keep the bounded inline path and offset paging ([#149](https://github.com/pvliesdonk/paperless-mcp/issues/149), [#165](https://github.com/pvliesdonk/paperless-mcp/pull/165)).

The Paperless request still includes OCR before the server removes it from the MCP response. That transport and memory cost remains open in [#164](https://github.com/pvliesdonk/paperless-mcp/issues/164).

## Paperless payload v10 and task resources

The client now requests Paperless payload v10 first. It retries with v9 only when Paperless returns the explicit invalid-version 406 response, then keeps that choice for the session. V10 task responses use an envelope and structured fields; the client translates v9's task filters and legacy field names when a 2.x instance requires the fallback. Saved-view visibility fields can now be `null` when v10 omits them ([#139](https://github.com/pvliesdonk/paperless-mcp/issues/139), [#161](https://github.com/pvliesdonk/paperless-mcp/pull/161)).

`tasks://paperless` now serializes timestamps through Pydantic's JSON mode, so populated pages produce valid ISO 8601 strings instead of failing on a `datetime` value. Its scope remains the first page of unacknowledged tasks; `list_tasks` remains the paginated interface ([#160](https://github.com/pvliesdonk/paperless-mcp/issues/160), [#162](https://github.com/pvliesdonk/paperless-mcp/pull/162)). The legacy trigger mapping is pinned to Paperless 3.1.3's serializer, including `email_consume → auto_task` ([#163](https://github.com/pvliesdonk/paperless-mcp/pull/163)).

## Shared runtime and deployment baseline

This server now follows [fastmcp-server-template v9.0.0](https://github.com/pvliesdonk/fastmcp-server-template/releases/tag/v9.0.0) and [fastmcp-pvl-core v9.0.0](https://github.com/pvliesdonk/fastmcp-pvl-core/releases/tag/v9.0.0) ([#168](https://github.com/pvliesdonk/paperless-mcp/pull/168)). pvl-core owns the process logger and HTTP runner. Logs are JSON when stderr is not a terminal; set `PAPERLESS_MCP_LOG_FORMAT=rich` when a terminal-style stream is wanted. `PAPERLESS_MCP_LOG_LEVEL` is the prefixed level variable. `FASTMCP_LOG_LEVEL` remains a one-major fallback, while `FASTMCP_ENABLE_RICH_LOGGING` is removed.

Malformed operator configuration now raises one `ConfigurationError` line and stops the server. An explicitly selected auth mode with no provider also refuses to start. The new `PAPERLESS_MCP_SHUTDOWN_GRACE_S` setting controls the HTTP drain window and defaults to three seconds. pvl-core v9 also keeps operator URL credentials out of app origins and error messages ([v9.0.0 release notes](https://github.com/pvliesdonk/fastmcp-pvl-core/releases/tag/v9.0.0)).

The repository now carries a security policy. Bootstrap can enable private vulnerability reporting and Dependabot alerts; it can also request secret-scanning push protection where the repository plan supports it. The project and its published package metadata now use the MIT license ([LICENSE](https://pvliesdonk.github.io/paperless-mcp/unstable/LICENSE)).

## Upgrading

- Replace `FASTMCP_LOG_LEVEL` with `PAPERLESS_MCP_LOG_LEVEL`. The old name is accepted for one major release and logs a deprecation event.
- Remove `FASTMCP_ENABLE_RICH_LOGGING`. Use `PAPERLESS_MCP_LOG_FORMAT=rich` or `json`; when unset, the renderer chooses Rich for a terminal and JSON elsewhere.
- If `PAPERLESS_MCP_AUTH_MODE` is set explicitly, provide the complete provider configuration. v9 refuses to start when that mode resolves to no provider.
- Python consumers must accept `None` for `SavedView.show_on_dashboard` and `SavedView.show_in_sidebar`.
- HTTP/SSE operators who want full files or OCR Markdown must set `PAPERLESS_MCP_BASE_URL` and route `/transfer/`. Other deployments retain bounded inline OCR and offset paging.
