# MCP Tools

Paperless MCP exposes the following tools to MCP clients.

## Document tools

| Tool | Description |
|---|---|
| `list_documents` | List documents with optional filters; OCR `content` stripped by default (`include_content=True` to opt in) |
| `search_documents` | Full-text and filtered document search; OCR `content` stripped by default (`include_content=True` to opt in) |
| `get_document` | Retrieve document metadata by ID |
| `get_document_content` | Retrieve the plain-text content of a document |
| `create_document` | Upload a new document for ingestion |
| `update_document` | Patch document metadata (title, tags, correspondent, etc.) |
| `delete_document` | Permanently delete a document |
| `bulk_edit_documents` | Apply a bulk operation to multiple documents |
| `get_document_notes` | List notes attached to a document |
| `add_document_note` | Add a note to a document |
| `get_document_history` | Retrieve audit log for a document |
| `create_download_link` | Generate a time-limited download URL |

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

## Document type tools

| Tool | Description |
|---|---|
| `list_document_types` | List all document types |
| `get_document_type` | Get a document type by ID |
| `create_document_type` | Create a new document type |
| `update_document_type` | Update a document type |
| `delete_document_type` | Delete a document type |

## Custom field tools

| Tool | Description |
|---|---|
| `list_custom_fields` | List all custom fields |
| `get_custom_field` | Get a custom field by ID |
| `create_custom_field` | Create a new custom field |
| `update_custom_field` | Update a custom field |
| `delete_custom_field` | Delete a custom field |

### extra_data by data_type

The `extra_data` field shape depends on the custom field's `data_type`. Refer to these shapes when using `create_custom_field` and `update_custom_field`:

| `data_type` | `extra_data` shape / example | Notes |
|---|---|---|
| `string`, `longtext`, `integer`, `boolean`, `float`, `date`, `url`, `documentlink` | — (unused) | Omit or pass `null` |
| `monetary` | `{"default_currency": "USD"}` | Optional ISO-4217 currency code; Paperless accepts `null`/absent |
| `select` | `{"select_options": [{"label": "Low"}, {"label": "Medium"}]}` | **Required** on create. Paperless assigns each option a stable `id` on creation. On update, re-use existing `id` values to preserve document values. |

Unknown shapes are rejected by Paperless with a 400 error.

## Share link tools

| Tool | Description |
|---|---|
| `list_share_links` | List share links (optionally filtered by document) |
| `get_share_link` | Fetch a share link by ID |

Both tools include a `share_url` field of the form `<PAPERLESS_PUBLIC_URL>/share/<slug>`.
`PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` is used when set; otherwise it defaults to
`PAPERLESS_MCP_PAPERLESS_URL` via the config layer (see `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL`
in the README env-var table).

## Task tools

| Tool | Description |
|---|---|
| `list_tasks` | List background Celery tasks. Paginates (`page`, `page_size` up to 100). Defaults to unacknowledged tasks only — pass `include_acknowledged=True` to include acknowledged tasks, or `acknowledged=True` to return only acknowledged ones. |
| `get_task` | Get a task by UUID |
| `wait_for_task` | Poll until a task reaches a terminal state or times out |

## System tools

| Tool | Description |
|---|---|
| `get_statistics` | Retrieve Paperless system statistics |
| `get_remote_version` | Check the Paperless-NGX version and update status |
