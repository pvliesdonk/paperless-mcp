# Paperless MCP

Paperless-NGX document management over MCP: search, tag, upload, and read documents; manage tags, correspondents, document types, and custom fields.

## Quick start

```bash
pip install pvliesdonk-paperless-mcp
paperless-mcp serve                                # stdio
paperless-mcp serve --transport http --port 8000   # HTTP
```

## Configuration

All settings come from environment variables with the `PAPERLESS_MCP_` prefix.

### Required

| Variable | Description |
|---|---|
| `PAPERLESS_MCP_PAPERLESS_URL` | Base URL of the Paperless-NGX REST API (no trailing slash). |
| `PAPERLESS_MCP_API_TOKEN` | Paperless service-account token. |

### Optional (with defaults)

| Variable | Default | Description |
|---|---|---|
| `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` | `30` | Per-request HTTP timeout (seconds). |
| `PAPERLESS_MCP_HTTP_RETRIES` | `2` | Retries (not counting the initial attempt) on 5xx/network errors. |
| `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` | `300` | TTL of URLs issued by `create_download_link`. Clamped `[30, 3600]`. |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE` | `25` | Default `page_size` for list tools. Clamped `[1, 100]`. |
| `PAPERLESS_MCP_READ_ONLY` | `false` | When `true`, disables every writable tool. |
| `PAPERLESS_MCP_INSTRUCTIONS` | *(built-in)* | Operator-supplied description appended to MCP instructions. |

See the [template's README section](#transport--auth) for transport (`TRANSPORT`, `HOST`, `PORT`, `HTTP_PATH`, `BASE_URL`), OIDC auth (`OIDC_*`), bearer fallback (`BEARER_TOKEN`), and logging (`LOG_LEVEL`, `LOG_FORMAT`) variables — those are inherited unchanged from `fastmcp-server-template`.

## Tools

### Documents

| Tool | Description |
|---|---|
| `list_documents` | List documents with optional filtering |
| `search_documents` | Full-text search across documents |
| `get_document` | Retrieve a document by ID |
| `get_document_content` | Get the extracted text content of a document |
| `get_document_thumbnail` | Get the thumbnail image of a document |
| `get_document_metadata` | Get metadata (original filename, checksums, etc.) |
| `get_document_notes` | List notes attached to a document |
| `get_document_history` | Get the audit history of a document |
| `get_document_suggestions` | Get AI-generated tag/correspondent/type suggestions |
| `update_document` | Update document fields (title, tags, correspondent, etc.) |
| `delete_document` | Delete a document |
| `upload_document` | Upload a new document for processing |
| `bulk_edit_documents` | Apply a bulk operation to multiple documents |
| `add_document_note` | Add a note to a document |
| `delete_document_note` | Delete a note from a document |

### Tags

| Tool | Description |
|---|---|
| `list_tags` | List all tags |
| `get_tag` | Get a tag by ID |
| `create_tag` | Create a new tag |
| `update_tag` | Update a tag |
| `delete_tag` | Delete a tag |
| `bulk_edit_tags` | Bulk edit tags |

### Correspondents

| Tool | Description |
|---|---|
| `list_correspondents` | List all correspondents |
| `get_correspondent` | Get a correspondent by ID |
| `create_correspondent` | Create a new correspondent |
| `update_correspondent` | Update a correspondent |
| `delete_correspondent` | Delete a correspondent |
| `bulk_edit_correspondents` | Bulk edit correspondents |

### Document Types

| Tool | Description |
|---|---|
| `list_document_types` | List all document types |
| `get_document_type` | Get a document type by ID |
| `create_document_type` | Create a new document type |
| `update_document_type` | Update a document type |
| `delete_document_type` | Delete a document type |
| `bulk_edit_document_types` | Bulk edit document types |

### Custom Fields

| Tool | Description |
|---|---|
| `list_custom_fields` | List all custom fields |
| `get_custom_field` | Get a custom field by ID |
| `create_custom_field` | Create a new custom field |
| `update_custom_field` | Update a custom field |
| `delete_custom_field` | Delete a custom field |
| `bulk_edit_custom_fields` | Bulk edit custom fields |

### Observability

| Tool | Description |
|---|---|
| `list_storage_paths` | List storage paths |
| `get_storage_path` | Get a storage path by ID |
| `list_saved_views` | List saved views |
| `get_saved_view` | Get a saved view by ID |
| `list_share_links` | List share links |
| `get_share_link` | Get a share link by ID |
| `list_tasks` | List background tasks |
| `get_task` | Get a task by ID |
| `wait_for_task` | Wait until a task completes |
| `get_statistics` | Get server statistics |
| `get_remote_version` | Get the Paperless-NGX version |

### Downloads

| Tool | Description |
|---|---|
| `create_download_link` | Create a time-limited download URL for a document |

## Resources

| URI | Description |
|---|---|
| `config://paperless` | Server configuration snapshot |
| `stats://paperless` | Document statistics |
| `remote-version://paperless` | Paperless-NGX version |
| `tags://paperless` | All tags |
| `correspondents://paperless` | All correspondents |
| `document-types://paperless` | All document types |
| `custom-fields://paperless` | All custom fields |
| `storage-paths://paperless` | All storage paths |
| `saved-views://paperless` | All saved views |
| `tasks://paperless` | All background tasks |
| `paperless://documents/{id}` | Document by ID |
| `paperless://documents/{id}/content` | Extracted text content |
| `paperless://documents/{id}/metadata` | File metadata |
| `paperless://documents/{id}/notes` | Document notes |
| `paperless://documents/{id}/history` | Audit history |
| `paperless://documents/{id}/thumbnail` | Thumbnail image |
| `paperless://documents/{id}/preview` | PDF preview |
| `paperless://documents/{id}/download` | Original file download |

## Links

- [Documentation](https://pvliesdonk.github.io/paperless-mcp/)
- [FastMCP](https://gofastmcp.com)
- [fastmcp-pvl-core](https://pypi.org/project/fastmcp-pvl-core/)
