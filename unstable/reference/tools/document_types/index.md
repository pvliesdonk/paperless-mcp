# Document types

## `list_document_types`

**List Document Types.** Read-only. Idempotent. Reaches outside the server.

List document types; returns one page with their ids and names.

**Parameters**

| Name              | Type             | Default | Description                                                                                                      |
| ----------------- | ---------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| `page`            | `integer`        | `1`     | Page number, starting at 1.                                                                                      |
| `page_size`       | `integer`        | `25`    | Results per page, up to 100.                                                                                     |
| `ordering`        | `string \| null` | `null`  | Field to sort by, such as name; prefix it with - to sort descending (-name). Omit for Paperless's default order. |
| `name__icontains` | `string \| null` | `null`  | Keep only names that contain this text, ignoring case.                                                           |

**Returns**

`object`

## `get_document_type`

**Get Document Type.** Read-only. Idempotent. Reaches outside the server.

Get one document type by id.

**Parameters**

| Name               | Type      | Default  | Description |
| ------------------ | --------- | -------- | ----------- |
| `document_type_id` | `integer` | required |             |

**Returns**

`object`

## `create_document_type`

**Create Document Type.** Changes state, not destructive. Reaches outside the server.

Create a document type; returns it with its id.

**Parameters**

| Name   | Type     | Default  | Description |
| ------ | -------- | -------- | ----------- |
| `body` | `object` | required |             |

**Returns**

`object`

## `update_document_type`

**Update Document Type.** Changes state, not destructive. Idempotent. Reaches outside the server.

Change a document type's name or matching rule; returns the updated document type.

**Parameters**

| Name               | Type      | Default  | Description                |
| ------------------ | --------- | -------- | -------------------------- |
| `document_type_id` | `integer` | required |                            |
| `patch`            | `object`  | required | Only the fields to change. |

**Returns**

`object`

## `delete_document_type`

**Delete Document Type.** Destructive. Idempotent. Reaches outside the server.

Delete a document type and clear it from every document of that type.

**Parameters**

| Name               | Type      | Default  | Description |
| ------------------ | --------- | -------- | ----------- |
| `document_type_id` | `integer` | required |             |

**Returns**

`null`

## `bulk_edit_document_types`

**Bulk Edit Document Types.** Destructive. Reaches outside the server.

Set the owner and permissions of many document types, or delete them; returns OK when applied.

**Parameters**

| Name         | Type                        | Default  | Description                                                                                                                                                                                                             |
| ------------ | --------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `operation`  | `set_permissions \| delete` | required | `set_permissions` or delete.                                                                                                                                                                                            |
| `ids`        | `array of integer`          | required | Ids of the objects to change.                                                                                                                                                                                           |
| `parameters` | `object \| null`            | `null`   | For `set_permissions`: owner (a user id or null), permissions ({"view": {"users": [ids], "groups": [ids]}, "change": {…}}) and merge (true adds to the current permissions instead of replacing them). Omit for delete. |

**Returns**

`object`
