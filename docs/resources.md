# Resources

The MCP resources this server registers are listed below. Collection resources
return the full set as JSON; document resources take a document ID.

<!-- DOMAIN-RESOURCES-LIST-START -->

## Collection resources

| URI | Description |
|---|---|
| `config://paperless` | Server configuration snapshot: the Paperless API URL, the public UI URL and the default page size for list tools |
| `stats://paperless` | Paperless-NGX document statistics |
| `remote-version://paperless` | The newest Paperless-NGX release published upstream, and whether it is newer than the connected instance. Not the version installed on it |
| `tags://paperless` | All tags |
| `correspondents://paperless` | All correspondents |
| `document-types://paperless` | All document types |
| `custom-fields://paperless` | All custom fields |
| `storage-paths://paperless` | All storage paths |
| `saved-views://paperless` | All saved views |
| `tasks://paperless` | All background tasks |

## Document resources

| URI | Description |
|---|---|
| `paperless://documents/{document_id}` | Document metadata by ID |
| `paperless://documents/{document_id}/content` | Extracted text content, in full. Resources take no arguments, so the character cap that `get_document_content` applies by default does not apply here. |
| `paperless://documents/{document_id}/metadata` | File metadata: original filename, checksums, MIME type |
| `paperless://documents/{document_id}/notes` | Notes attached to the document |
| `paperless://documents/{document_id}/history` | Audit history |
| `paperless://documents/{document_id}/thumbnail` | Thumbnail image |
| `paperless://documents/{document_id}/preview` | PDF preview |
| `paperless://documents/{document_id}/download` | Original file download |

<!-- DOMAIN-RESOURCES-LIST-END -->
