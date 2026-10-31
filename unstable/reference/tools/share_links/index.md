# Share links

Each link carries a `share_url` of the form `<public URL>/share/<slug>`, built from `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` when that's set, and from the API URL otherwise.

## `list_share_links`

**List Share Links.** Read-only. Idempotent. Reaches outside the server.

List public share links for documents; returns one page with each link's document, expiry and URL.

**Parameters**

| Name          | Type              | Default | Description                           |
| ------------- | ----------------- | ------- | ------------------------------------- |
| `page`        | `integer`         | `1`     | Page number, starting at 1.           |
| `page_size`   | `integer`         | `25`    | Results per page, up to 100.          |
| `document_id` | `integer \| null` | `null`  | Keep only the links to this document. |

**Returns**

`object`

## `get_share_link`

**Get Share Link.** Read-only. Idempotent. Reaches outside the server.

Get one share link by id, with its document, expiry and URL.

**Parameters**

| Name            | Type      | Default  | Description |
| --------------- | --------- | -------- | ----------- |
| `share_link_id` | `integer` | required |             |

**Returns**

`object`
