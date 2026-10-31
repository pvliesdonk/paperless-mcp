# Correspondents

## `list_correspondents`

**List Correspondents.** Read-only. Idempotent. Reaches outside the server.

List correspondents; returns one page with their ids and names.

Each carries `last_correspondence`, the date of its newest document.

**Parameters**

| Name              | Type             | Default | Description                                                                                                                                                          |
| ----------------- | ---------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `page`            | `integer`        | `1`     | Page number, starting at 1.                                                                                                                                          |
| `page_size`       | `integer`        | `25`    | Results per page, up to 100.                                                                                                                                         |
| `ordering`        | `string \| null` | `null`  | Field to sort by: name, `document_count` or `last_correspondence`; prefix it with - to sort descending (-`last_correspondence`). Omit for Paperless's default order. |
| `name__icontains` | `string \| null` | `null`  | Keep only names that contain this text, ignoring case.                                                                                                               |

**Returns**

`object`

## `get_correspondent`

**Get Correspondent.** Read-only. Idempotent. Reaches outside the server.

Get one correspondent by id.

**Parameters**

| Name               | Type      | Default  | Description |
| ------------------ | --------- | -------- | ----------- |
| `correspondent_id` | `integer` | required |             |

**Returns**

`object`

## `create_correspondent`

**Create Correspondent.** Changes state, not destructive. Reaches outside the server.

Create a correspondent; returns it with its id.

**Parameters**

| Name   | Type     | Default  | Description |
| ------ | -------- | -------- | ----------- |
| `body` | `object` | required |             |

**Returns**

`object`

## `update_correspondent`

**Update Correspondent.** Changes state, not destructive. Idempotent. Reaches outside the server.

Change a correspondent's name or matching rule; returns the updated correspondent.

**Parameters**

| Name               | Type      | Default  | Description                |
| ------------------ | --------- | -------- | -------------------------- |
| `correspondent_id` | `integer` | required |                            |
| `patch`            | `object`  | required | Only the fields to change. |

**Returns**

`object`

## `delete_correspondent`

**Delete Correspondent.** Destructive. Idempotent. Reaches outside the server.

Delete a correspondent and clear it from every document that names it.

**Parameters**

| Name               | Type      | Default  | Description |
| ------------------ | --------- | -------- | ----------- |
| `correspondent_id` | `integer` | required |             |

**Returns**

`null`

## `bulk_edit_correspondents`

**Bulk Edit Correspondents.** Destructive. Reaches outside the server.

Set the owner and permissions of many correspondents, or delete them; returns OK when applied.

**Parameters**

| Name         | Type                        | Default  | Description                                                                                                                                                                                                             |
| ------------ | --------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `operation`  | `set_permissions \| delete` | required | `set_permissions` or delete.                                                                                                                                                                                            |
| `ids`        | `array of integer`          | required | Ids of the objects to change.                                                                                                                                                                                           |
| `parameters` | `object \| null`            | `null`   | For `set_permissions`: owner (a user id or null), permissions ({"view": {"users": [ids], "groups": [ids]}, "change": {…}}) and merge (true adds to the current permissions instead of replacing them). Omit for delete. |

**Returns**

`object`
