# Docker Deployment

## Quick start

```bash
docker compose up -d
```

The server listens on port 8000 with HTTP transport by default.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PAPERLESS_MCP_READ_ONLY` | `true` | Disable write tools |
| `PAPERLESS_MCP_BEARER_TOKEN` | — | Enable bearer token auth |
| `PAPERLESS_MCP_LOG_LEVEL` | `INFO` | Log level |
| `PAPERLESS_MCP_INSTRUCTIONS` | (dynamic) | System instructions for LLM context |

For OIDC auth variables, see [Authentication](../guides/authentication.md).

## Volumes

| Path | Purpose |
|------|---------|
| `/data/service` | Your service data (bind-mount or named volume) |
| `/data/state` | State files (FastMCP OIDC state, etc.) |

## UID/GID

Set `PUID` and `PGID` in your `.env` file to match the owner of bind-mounted
directories (default 1000/1000).
