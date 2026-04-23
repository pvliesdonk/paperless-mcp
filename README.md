# Paperless MCP

Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.

## Quick start

```bash
pip install pvliesdonk-paperless-mcp
paperless-mcp serve                                # stdio
paperless-mcp serve --transport http --port 8000   # HTTP
```

## Configuration

All configuration goes via `PAPERLESS_MCP_*` env vars.  See
[docs/configuration.md](docs/configuration.md).

## Links

- [Documentation](https://pvliesdonk.github.io/paperless-mcp/)
- [FastMCP](https://gofastmcp.com)
- [fastmcp-pvl-core](https://pypi.org/project/fastmcp-pvl-core/)
