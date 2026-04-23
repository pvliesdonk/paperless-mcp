# Paperless MCP

Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.

## Quick start

```bash
pip install pvliesdonk-paperless-mcp
paperless-mcp serve                                # stdio
paperless-mcp serve --transport http --port 8000   # HTTP
```

## What it does

Paperless MCP exposes your [Paperless-NGX](https://docs.paperless-ngx.com/) instance as a set of MCP tools and resources, letting AI assistants:

- **Search** documents by full-text query, tags, correspondent, date range, and more
- **Read** document content, metadata, notes, and history
- **Upload** new documents and monitor ingestion tasks
- **Manage** tags, correspondents, document types, custom fields, and storage paths

## Configuration

All configuration goes via `PAPERLESS_MCP_*` environment variables. See [Configuration](configuration.md).

## Links

- [FastMCP](https://gofastmcp.com)
- [Paperless-NGX](https://docs.paperless-ngx.com/)
- [GitHub](https://github.com/pvliesdonk/paperless-mcp)
