# Custom fields

The shape of `extra_data` in `create_custom_field` and `update_custom_field` depends on the field's type:

| Type                                                                               | `extra_data`                                                  | Notes                                                                                                                                                                                                                                             |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `string`, `longtext`, `integer`, `boolean`, `float`, `date`, `url`, `documentlink` | unused                                                        | Omit it or pass `null`.                                                                                                                                                                                                                           |
| `monetary`                                                                         | `{"default_currency": "USD"}`                                 | An optional ISO 4217 currency code; Paperless also accepts `null` or no value.                                                                                                                                                                    |
| `select`                                                                           | `{"select_options": [{"label": "Low"}, {"label": "Medium"}]}` | Required on create. Paperless gives each option a stable `id`; on update, reuse the existing ids to keep documents' values. A patch without `extra_data`, such as a rename, keeps the current options: the server reads them and sends them back. |

Paperless rejects any other shape with a 400.

## `list_custom_fields`

**List Custom Fields.** Read-only. Idempotent. Reaches outside the server.

List custom field definitions; returns one page with their ids, names and types.

**Parameters**

| Name        | Type             | Default | Description                                                                                                      |
| ----------- | ---------------- | ------- | ---------------------------------------------------------------------------------------------------------------- |
| `page`      | `integer`        | `1`     | Page number, starting at 1.                                                                                      |
| `page_size` | `integer`        | `25`    | Results per page, up to 100.                                                                                     |
| `ordering`  | `string \| null` | `null`  | Field to sort by, such as name; prefix it with - to sort descending (-name). Omit for Paperless's default order. |

**Returns**

`object`

## `get_custom_field`

**Get Custom Field.** Read-only. Idempotent. Reaches outside the server.

Get one custom field definition by id, with its select options.

**Parameters**

| Name       | Type      | Default  | Description |
| ---------- | --------- | -------- | ----------- |
| `field_id` | `integer` | required |             |

**Returns**

`object`

## `create_custom_field`

**Create Custom Field.** Changes state, not destructive. Reaches outside the server.

Define a new custom field; returns it with its id.

**Parameters**

| Name   | Type     | Default  | Description                                                       |
| ------ | -------- | -------- | ----------------------------------------------------------------- |
| `body` | `object` | required | The field's name, type and, for select or monetary, `extra_data`. |

**Returns**

`object`

## `update_custom_field`

**Update Custom Field.** Changes state, not destructive. Idempotent. Reaches outside the server.

Rename a custom field or change its options; returns the updated field.

**Parameters**

| Name       | Type      | Default  | Description                |
| ---------- | --------- | -------- | -------------------------- |
| `field_id` | `integer` | required |                            |
| `patch`    | `object`  | required | Only the fields to change. |

**Returns**

`object`

## `delete_custom_field`

**Delete Custom Field.** Destructive. Idempotent. Reaches outside the server.

Delete a custom field and its value on every document.

**Parameters**

| Name       | Type      | Default  | Description |
| ---------- | --------- | -------- | ----------- |
| `field_id` | `integer` | required |             |

**Returns**

`null`
