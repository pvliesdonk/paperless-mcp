# Command line

Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.

## `paperless-mcp serve`

Run the MCP server.

| Option        | Env var | Default | Description                                                          |
| ------------- | ------- | ------- | -------------------------------------------------------------------- |
| `--transport` |         | stdio   | MCP transport (stdio / http / sse).                                  |
| `--host`      |         |         | Bind host (http only; default: $`PAPERLESS_MCP_HOST` or 127.0.0.1).  |
| `--port`      |         |         | Bind port (http only; default: $`PAPERLESS_MCP_PORT` or 8000).       |
| `--http-path` |         |         | Mount path (http only, default: $`PAPERLESS_MCP_HTTP_PATH` or /mcp). |
