# Resources

The MCP resources this server registers are listed below. Collection resources return JSON; document resources take a document ID.

## Collection resources

| URI                          | Description                                                                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `config://paperless`         | Server configuration snapshot: the Paperless API URL, the public UI URL and the default page size for list tools                          |
| `stats://paperless`          | Paperless-NGX document statistics                                                                                                         |
| `remote-version://paperless` | The newest Paperless-NGX release published upstream, and whether it is newer than the connected instance. Not the version installed on it |
| `tags://paperless`           | All tags                                                                                                                                  |
| `correspondents://paperless` | All correspondents, each with `last_correspondence`                                                                                       |
| `document-types://paperless` | All document types                                                                                                                        |
| `custom-fields://paperless`  | All custom fields                                                                                                                         |
| `storage-paths://paperless`  | All storage paths                                                                                                                         |
| `saved-views://paperless`    | All saved views                                                                                                                           |
| `tasks://paperless`          | First page of unacknowledged background tasks                                                                                             |

The task resource returns a JSON array. Task timestamps are ISO 8601 strings; missing timestamps are `null`. Use the `list_tasks` tool to request further pages or filter tasks.

## Document resources

| URI                                             | Description                                                                                                                                   |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `paperless://documents/{document_id}`           | Document metadata by ID, without OCR content                                                                                                  |
| `paperless://documents/{document_id}/content`   | First 20,000 characters of extracted text. A partial result points to `get_document_content` for paging and to transfer links when available. |
| `paperless://documents/{document_id}/metadata`  | File metadata: original filename, checksums, MIME type                                                                                        |
| `paperless://documents/{document_id}/notes`     | Notes attached to the document                                                                                                                |
| `paperless://documents/{document_id}/history`   | Audit history                                                                                                                                 |
| `paperless://documents/{document_id}/thumbnail` | Thumbnail image                                                                                                                               |

On HTTP deployments with `PAPERLESS_MCP_BASE_URL`, original files, archived PDF files, and previews are available through `create_download_link`. Returning whole files as resources puts their bytes in model context, so the inline preview and download resources are not registered.
