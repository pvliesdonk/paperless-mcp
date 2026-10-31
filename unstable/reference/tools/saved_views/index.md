# Saved views

`show_on_dashboard` and `show_in_sidebar` are `null` when Paperless omits them, as payload version 10 does. The values are unknown, not false.

## `list_saved_views`

**List Saved Views.** Read-only. Idempotent. Reaches outside the server.

List saved views, the named document filters users keep in Paperless; returns one page.

**Parameters**

| Name        | Type      | Default | Description                  |
| ----------- | --------- | ------- | ---------------------------- |
| `page`      | `integer` | `1`     | Page number, starting at 1.  |
| `page_size` | `integer` | `25`    | Results per page, up to 100. |

**Returns**

`object`

## `get_saved_view`

**Get Saved View.** Read-only. Idempotent. Reaches outside the server.

Get one saved view by id, with its filter rules and sort order.

**Parameters**

| Name      | Type      | Default  | Description |
| --------- | --------- | -------- | ----------- |
| `view_id` | `integer` | required |             |

**Returns**

`object`
