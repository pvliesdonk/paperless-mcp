# Storage paths

## `list_storage_paths`

**List Storage Paths.** Read-only. Idempotent. Reaches outside the server.

List storage paths, the folder layouts Paperless files documents into; returns one page.

**Parameters**

| Name        | Type             | Default | Description                                                                                                      |
| ----------- | ---------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| `page`      | `integer`        | `1`     | Page number, starting at 1.                                                                                      |
| `page_size` | `integer`        | `25`    | Results per page, up to 100.                                                                                     |
| `ordering`  | `string \| null` | `null`  | Field to sort by, such as name; prefix it with - to sort descending (-name). Omit for Paperless's default order. |

**Returns**

`object`

## `get_storage_path`

**Get Storage Path.** Read-only. Idempotent. Reaches outside the server.

Get one storage path by id, with its path template.

**Parameters**

| Name              | Type      | Default  | Description |
| ----------------- | --------- | -------- | ----------- |
| `storage_path_id` | `integer` | required |             |

**Returns**

`object`
