# Transfer links

This server has transfer links when `create_download_link` and `create_upload_link` appear in the [tools reference](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/tools/index.md). A transfer link is a one-time URL for one file. The bytes travel over plain HTTP between the server and whoever holds the link; the conversation carries only the URL and its expiry, so a large file never passes through the model. The link route sits outside authentication, which makes the URL itself the credential: the [security model](https://pvliesdonk.github.io/paperless-mcp/unstable/security-model/index.md) says what the tools behind it reach.

## For the person holding a link

A tool call returns `url` and `expires_in_s`. A download link answers one `GET`; the response carries the file as an attachment, so a browser saves it rather than showing it:

```
curl -o report.pdf "https://mcp.example.com/transfer/<token>"
```

An upload link takes the file's bytes as the request body of one `POST` (or `PUT`), raw, not as a form:

```
curl -X POST --data-binary @diagram.png "https://mcp.example.com/transfer/<token>"
```

What the answers mean:

| Status | Meaning                                                                                                                                                           |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `200`  | The transfer happened. For a short grace window the same link still answers, so a download that stalled part-way can be fetched again; after it the link is gone. |
| `404`  | No such link: unknown, expired, already used, or minted for the other direction. The server does not say which.                                                   |
| `409`  | Another request is using this link at this moment; retry shortly.                                                                                                 |
| `413`  | The upload is larger than the server accepts; the link stays usable for a smaller one.                                                                            |

Where the file goes on an upload is fixed when the link is minted; whoever uploads cannot change it.

## For the operator

- **The route.** `/transfer/{token}` is registered beside the MCP endpoint and outside the authentication middleware. No bearer token or sign-in is asked for; the token in the URL is the authorization. It is 256 bits of randomness. A used or expired link answers like one that never existed.
- **The public URL.** Links are built from `PAPERLESS_MCP_BASE_URL`, which the server requires before it registers the route at all; under a path prefix the link carries the prefix, so the [reverse proxy](https://pvliesdonk.github.io/paperless-mcp/unstable/deploy/reverse-proxy/#a-path-prefix) must route `/transfer/` to the server the same way it routes the MCP path. Stdio has no route: the tools are absent there, not failing.
- **The store.** Tokens live in the server's key-value store (`PAPERLESS_MCP_KV_STORE_URL`), so replicas that share the store share the links.
- **The variables.** The five settings below are read from the environment under this server's prefix; the [configuration reference](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/configuration/index.md) carries the authoritative list for this server, and the defaults here are fastmcp-pvl-core 10.1's.

| Variable                                  | Default     | Meaning                                                                             |
| ----------------------------------------- | ----------- | ----------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_TRANSFER_TTL_DEFAULT_S`    | `3600`      | Link lifetime when the caller gives none.                                           |
| `PAPERLESS_MCP_TRANSFER_TTL_MAX_S`        | `86400`     | Ceiling; a longer requested lifetime is capped to it.                               |
| `PAPERLESS_MCP_TRANSFER_GRACE_TTL_S`      | `60`        | How long a used link stays valid for a retry of a stalled transfer.                 |
| `PAPERLESS_MCP_TRANSFER_LEASE_S`          | `60`        | How long a transfer may hold the link before a crashed handler's claim is released. |
| `PAPERLESS_MCP_TRANSFER_MAX_UPLOAD_BYTES` | `104857600` | The per-upload size cap (100 MiB).                                                  |

A link pasted into a chat or written to a log is a live credential until it is used or expires, since nothing else guards the route. A shorter default lifetime narrows that window; the model can still ask for less with the tool's `ttl_s` argument, never for more than the ceiling.

### Paperless documents

A download link names a document and one of its files. `original` (the default) is the file as uploaded, `archive` the searchable PDF Paperless made, `preview` the rendition its web interface shows, and `content` the full text as a UTF-8 Markdown file. Asking for `archive` on a document without an archived PDF is refused when the link is created. A download reads the current file, so a change after the link was created shows in what it serves.

A `content` file opens with YAML front matter: the document id, title, created timestamp, correspondent id, document type id and tag ids. The text follows unchanged.

An upload link creates a new document, consumed like any Paperless upload. It takes PDF and every other file type the instance accepts, Markdown included, with its bytes and file name kept. Metadata goes in the link's reference: `title`, `correspondent`, `document_type`, `tags`, `created`, `archive_serial_number` and `custom_fields`. Front matter inside a Markdown file stays part of the file. The answer to an upload carries the consume task's id for `wait_for_task`. Sending the same bytes to the link again returns the same task id. A `409` also answers bytes that differ from an earlier upload on the link, or an earlier result the server can't confirm; check the Paperless tasks before creating another link.
