# Configuration

Paperless MCP is configured via environment variables with the
`PAPERLESS_MCP_` prefix.

## Common variables

See `fastmcp-pvl-core`'s README for the full list of universal
variables (`PAPERLESS_MCP_TRANSPORT`, `PAPERLESS_MCP_HOST`,
`PAPERLESS_MCP_PORT`, `PAPERLESS_MCP_HTTP_PATH`,
`PAPERLESS_MCP_BASE_URL`, auth vars, etc.).

## Server identity

- `PAPERLESS_MCP_SERVER_NAME` defaults to `paperless-mcp`.
- `PAPERLESS_MCP_INSTRUCTIONS` replaces the default MCP instructions text.

<!-- DOMAIN-CONFIG-VARS-START -->
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
| `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` | `300` | TTL for download URLs issued by `create_download_link` (clamped 30-3600) |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` | `25` | Default page size for list tools (clamped 1-100) |

## Public URL

`PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` lets you specify a different base URL for
user-visible links than the internal API URL used by the server. When unset, it
defaults to `PAPERLESS_MCP_PAPERLESS_URL`; trailing slashes are stripped.

## Example `.env`

```bash
PAPERLESS_MCP_PAPERLESS_URL=http://paperless.local:8000
PAPERLESS_MCP_API_TOKEN=abc123yourtokenhere
PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS=60
PAPERLESS_MCP_DEFAULT_PAGE_SIZE=50
```
<!-- DOMAIN-CONFIG-VARS-END -->
