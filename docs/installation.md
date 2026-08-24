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

<<<<<<< before updating
See [Docker deployment](deployment/docker.md) for full options.

## Verify installation

```bash
paperless-mcp --version
=======
The `latest` tag is the newest stable release. The rolling `edge` tag tracks every merge to `main` and carries no version identity; see [Image tags](deployment/docker.md#image-tags) for the full list.

## From source

```bash
git clone https://github.com/pvliesdonk/paperless-mcp
cd paperless-mcp
uv sync --all-extras --all-groups
>>>>>>> after updating
```

<!-- DOMAIN-INSTALL-EXTRA-START -->
<!-- Project-specific notes for installation go here; kept across copier
     update. (E.g. system dependencies, optional extras, custom configuration
     steps.) -->
<!-- DOMAIN-INSTALL-EXTRA-END -->
