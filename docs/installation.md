# Installation

## Requirements

- Python 3.11 or later
- A running [Paperless-NGX](https://docs.paperless-ngx.com/) instance (v1.17+)
- A Paperless API token (Settings → API Token in the Paperless web UI)

## pip / uv

```bash
pip install pvliesdonk-paperless-mcp
# or
uv tool install pvliesdonk-paperless-mcp
```

## Docker

```bash
docker run --rm \
  -e PAPERLESS_MCP_PAPERLESS_URL=http://paperless:8000 \
  -e PAPERLESS_MCP_API_TOKEN=your-token \
  ghcr.io/pvliesdonk/paperless-mcp:latest
```

See [Docker deployment](deployment/docker.md) for full options.

## Verify installation

```bash
paperless-mcp --version
```
