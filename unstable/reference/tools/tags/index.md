# Tags

## `list_tags`

**List Tags.** Read-only. Idempotent. Reaches outside the server.

List tags; returns one page with their ids and names.

**Parameters**

| Name              | Type             | Default | Description                                                                                                      |
| ----------------- | ---------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| `page`            | `integer`        | `1`     | Page number, starting at 1.                                                                                      |
| `page_size`       | `integer`        | `25`    | Results per page, up to 100.                                                                                     |
| `ordering`        | `string \| null` | `null`  | Field to sort by, such as name; prefix it with - to sort descending (-name). Omit for Paperless's default order. |
| `name__icontains` | `string \| null` | `null`  | Keep only names that contain this text, ignoring case.                                                           |

**Returns**

`object`

## `get_tag`

**Get Tag.** Read-only. Idempotent. Reaches outside the server.

Get one tag by id.

**Parameters**

| Name     | Type      | Default  | Description |
| -------- | --------- | -------- | ----------- |
| `tag_id` | `integer` | required |             |

**Returns**

`object`

## `create_tag`

**Create Tag.** Changes state, not destructive. Reaches outside the server.

Create a tag; returns it with its id.

**Parameters**

| Name   | Type     | Default  | Description |
| ------ | -------- | -------- | ----------- |
| `body` | `object` | required |             |

**Returns**

`object`

## `update_tag`

**Update Tag.** Changes state, not destructive. Idempotent. Reaches outside the server.

Change a tag's name, colour, inbox flag or matching rule; returns the tag.

**Parameters**

| Name     | Type      | Default  | Description                |
| -------- | --------- | -------- | -------------------------- |
| `tag_id` | `integer` | required |                            |
| `patch`  | `object`  | required | Only the fields to change. |

**Returns**

`object`

## `delete_tag`

**Delete Tag.** Destructive. Idempotent. Reaches outside the server.

Delete a tag and remove it from every document that carries it.

**Parameters**

| Name     | Type      | Default  | Description |
| -------- | --------- | -------- | ----------- |
| `tag_id` | `integer` | required |             |

**Returns**

`null`

## `bulk_edit_tags`

**Bulk Edit Tags.** Destructive. Reaches outside the server.

Set the owner and permissions of many tags, or delete them; returns OK when applied.

**Parameters**

| Name         | Type                        | Default  | Description                                                                                                                                                                                                             |
| ------------ | --------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `operation`  | `set_permissions \| delete` | required | `set_permissions` or delete.                                                                                                                                                                                            |
| `ids`        | `array of integer`          | required | Ids of the objects to change.                                                                                                                                                                                           |
| `parameters` | `object \| null`            | `null`   | For `set_permissions`: owner (a user id or null), permissions ({"view": {"users": [ids], "groups": [ids]}, "change": {…}}) and merge (true adds to the current permissions instead of replacing them). Omit for delete. |

**Returns**

`object`
