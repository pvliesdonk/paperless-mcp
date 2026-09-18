# Tools

The tools registered in this server are listed below.

Every tool also carries a human-readable title, which clients that support
titles show in place of the machine name. A few titles say what the tool does
rather than restating its name: `get_remote_version` is titled **Check for
Paperless Updates**, and `get_document_metadata` is titled **Get Document File
Details**. The tables below list machine names, which is what you pass when
calling a tool.

<!-- DOMAIN-TOOLS-LIST-START -->

## Document tools

| Tool | Description |
|---|---|
| `list_documents` | List documents with optional filters; OCR `content` stripped by default (`include_content=True` to opt in). `notes[].note` and `custom_fields[].value` are always stripped. Fetch them via single-document endpoints. |
| `search_documents` | Full-text and filtered document search; OCR `content` stripped by default (`include_content=True` to opt in). `notes[].note` and `custom_fields[].value` are always stripped on hits. |
| `get_document` | Retrieve document metadata by ID; OCR `content` stripped by default (`include_content=True` to opt in) |
| `get_document_content` | Retrieve the plain-text content of a document; capped at 50,000 characters by default (`max_chars=None` for the full text). A capped result names the range returned and the `offset` to pass to read the next section. |
| `upload_document` | Upload a new document for ingestion |
| `update_document` | Patch document metadata (title, tags, correspondent, etc.) |
| `delete_document` | Permanently delete a document |
| `bulk_edit_documents` | Apply a bulk operation to multiple documents |
| `get_document_metadata` | Retrieve file metadata: original filename, checksums, MIME type |
| `get_document_thumbnail` | Retrieve the thumbnail image of a document |
| `get_document_suggestions` | Retrieve the tags, correspondent and type Paperless suggests for a document |
| `get_document_notes` | List notes attached to a document |
| `add_document_note` | Add a note to a document |
| `delete_document_note` | Delete a note from a document |
| `get_document_history` | Retrieve audit log for a document |

`get_document`, `list_documents`, `search_documents`, and `update_document` include a `web_url` field pointing to the document in the Paperless UI, such as `https://paperless.example.com/documents/42/`. Set `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` if the public URL differs from the API URL; otherwise the API URL is used.

### Pagination

All paginated tools return `next`/`previous` as bare `page=N` markers (or `None`). Upstream Paperless URLs are normalised away so the internal hostname never leaks into MCP responses. Both server-paginated (documents, tags, and similar endpoints) and client-paginated (tasks) endpoints now share a single shape. Callers pass `page=N` explicitly to fetch subsequent pages.

## Tag tools

| Tool | Description |
|---|---|
| `list_tags` | List all tags |
| `get_tag` | Get a tag by ID |
| `create_tag` | Create a new tag |
| `update_tag` | Update a tag |
| `delete_tag` | Delete a tag |
| `bulk_edit_tags` | Bulk-add or remove tags across documents |

## Correspondent tools

| Tool | Description |
|---|---|
| `list_correspondents` | List all correspondents |
| `get_correspondent` | Get a correspondent by ID |
| `create_correspondent` | Create a new correspondent |
| `update_correspondent` | Update a correspondent |
| `delete_correspondent` | Delete a correspondent |
| `bulk_edit_correspondents` | Apply a bulk operation across correspondents |

## Document type tools

| Tool | Description |
|---|---|
| `list_document_types` | List all document types |
| `get_document_type` | Get a document type by ID |
| `create_document_type` | Create a new document type |
| `update_document_type` | Update a document type |
| `delete_document_type` | Delete a document type |
| `bulk_edit_document_types` | Apply a bulk operation across document types |

## Custom field tools

| Tool | Description |
|---|---|
| `list_custom_fields` | List all custom fields |
| `get_custom_field` | Get a custom field by ID |
| `create_custom_field` | Create a new custom field |
| `update_custom_field` | Update a custom field |
| `delete_custom_field` | Delete a custom field |

### Additional data by type

The additional-data field shape depends on the custom field type. Refer to these shapes when using `create_custom_field` and `update_custom_field`:

| Type | Additional-data shape / example | Notes |
|---|---|---|
| `string`, `longtext`, `integer`, `boolean`, `float`, `date`, `url`, `documentlink` | (unused) | Omit or pass `null` |
| `monetary` | `{"default_currency": "USD"}` | Optional ISO-4217 currency code; Paperless accepts `null`/absent |
| `select` | `{"select_options": [{"label": "Low"}, {"label": "Medium"}]}` | **Required** on create. Paperless assigns each option a stable `id` on creation. On update, re-use existing `id` values to preserve document values. |

Unknown shapes are rejected by Paperless with a 400 error.

## Storage path tools

| Tool | Description |
|---|---|
| `list_storage_paths` | List all storage paths |
| `get_storage_path` | Get a storage path by ID |

## Saved view tools

| Tool | Description |
|---|---|
| `list_saved_views` | List all saved views |
| `get_saved_view` | Get a saved view by ID |

## Share link tools

| Tool | Description |
|---|---|
| `list_share_links` | List share links (optionally filtered by document) |
| `get_share_link` | Fetch a share link by ID |

Both tools include a `share_url` field of the form `<PAPERLESS_MCP_PAPERLESS_PUBLIC_URL>/share/<slug>`.
`PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` is used when set; otherwise it defaults to
`PAPERLESS_MCP_PAPERLESS_URL` via the config layer (see
[Configuration](../configuration.md) for the variable).

## Task tools

| Tool | Description |
|---|---|
| `list_tasks` | List background Celery tasks. Paginates (`page`, `page_size` up to 100). Defaults to unacknowledged tasks only. Pass `include_acknowledged=True` to include acknowledged tasks, or `acknowledged=True` to return only acknowledged ones. |
| `get_task` | Get a task by UUID |
| `wait_for_task` | Poll until a task reaches a terminal state or times out |

## System tools

| Tool | Description |
|---|---|
| `get_statistics` | Retrieve Paperless system statistics |
| `get_remote_version` | Check whether a newer Paperless-NGX release exists upstream: the newest release published on GitHub, and whether it is newer than the connected instance. Not the installed version (see `get_server_info`) |
| `get_server_info` | Report this server's own build and the version installed on the Paperless instance it talks to |

`get_server_info` answers "is the deployed build the one I expect, and against
which Paperless?" in one call. It returns `server_name`, `server_version`,
`core_version` (the `fastmcp-pvl-core` version), and a `paperless` block
carrying the version **installed on the instance this server is connected to**:

```json
{
  "server_name": "paperless-mcp",
  "server_version": "1.0.2",
  "core_version": "7.2.0",
  "paperless": {"version": "2.14.7"}
}
```

An instance running 2.14.7 reports `2.14.7` here whether or not a newer release
exists. For the newer release, call `get_remote_version`. The same instance can
report different numbers from the two tools:

| Question | Tool | Answer for the instance above |
|---|---|---|
| Which Paperless am I connected to? | `get_server_info` | `2.14.7` |
| Is there a newer Paperless to upgrade to? | `get_remote_version` | `2.20.14`, `update_available: true` |

When Paperless cannot answer, the `paperless` block is `{"version": null}` and
the rest of the response is unaffected. The version is extra information about
a call whose job is reporting this server's build, so it never fails that call.
Paperless cannot answer when it is down, when the URL is wrong, when the token
is rejected, and also when the token's Paperless user lacks permission to view
UI settings, which is where this version is published. Grant that user the
"view" permission on UI settings if you want the version reported; everything
else the server does is unaffected either way.
<!-- DOMAIN-TOOLS-LIST-END -->
