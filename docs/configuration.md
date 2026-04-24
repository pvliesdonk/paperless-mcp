# Configuration

All configuration is provided via environment variables with the `PAPERLESS_MCP_` prefix.

## Required variables

| Variable | Description |
|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | Base URL of the Paperless-NGX instance (no trailing slash). Example: `http://paperless:8000` |
| `PAPERLESS_MCP_API_TOKEN` | Paperless service-account API token |

## Optional variables

| Variable | Default | Description |
|---|---|---|
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | *(same as `PAPERLESS_MCP_PAPERLESS_URL`)* | Public-facing Paperless UI URL. See [Public URL](#public-url) below. |
| `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` | `30.0` | Per-request timeout (connect + read + write) |
| `PAPERLESS_MCP_HTTP_RETRIES` | `2` | Retry count for idempotent requests on network errors or 5xx |
| `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` | `300` | TTL for download URLs issued by `create_download_link` (clamped 30–3600) |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` | `25` | Default page size for list tools (clamped 1–100) |

## Public URL

`PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` lets you specify a different base URL for
user-visible links (e.g. the `web_url` field on documents and the `share_url`
field on share links) than the internal API URL used by the server.

This is useful when Paperless-NGX is reachable by the MCP server at an internal
address (e.g. `http://paperless:8000`) but documents should link to a public
hostname (e.g. `https://docs.example.com`).

When unset, it defaults to `PAPERLESS_MCP_PAPERLESS_URL`.  Trailing slashes are
stripped automatically, consistent with `PAPERLESS_MCP_PAPERLESS_URL`.

```bash
PAPERLESS_MCP_PAPERLESS_URL=http://paperless:8000        # internal API URL
PAPERLESS_MCP_PAPERLESS_PUBLIC_URL=https://docs.example.com  # public UI URL
```

## Example `.env`

```bash
PAPERLESS_MCP_PAPERLESS_URL=http://paperless.local:8000
PAPERLESS_MCP_API_TOKEN=abc123yourtokenhere
PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS=60
PAPERLESS_MCP_DEFAULT_PAGE_SIZE=50
```

## Log level

Set `FASTMCP_LOG_LEVEL` to `DEBUG`, `INFO`, `WARNING`, or `ERROR`.
Pass `-v` / `--verbose` to the CLI to enable `DEBUG` automatically.
