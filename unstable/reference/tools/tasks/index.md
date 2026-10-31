# Tasks

On payload version 10, task pages come from Paperless directly and carry `task_type`, `trigger_source`, `result_data`, `related_document_ids`, `date_started`, `duration_seconds` and `wait_time_seconds`. Version 9 can't supply the timing and result fields, so they stay `null` rather than being guessed from the result text, and its task arrays are paginated by this server into the same page shape. Status values keep Paperless's uppercase spelling.

The `status` and `task_type` filters use the version 10 names on either version; on version 9 this server translates them to that version's spelling. A `task_type` filter only matches kinds the connected instance records, and not every kind exists on Paperless 2.x.

The older `task_name`, `type`, `result`, `task_file_name` and `related_document` fields remain for compatibility. `related_document` names only the first related document; use `related_document_ids` for all of them.

## `list_tasks`

**List Background Tasks.** Read-only. Idempotent. Reaches outside the server.

List Paperless background tasks such as consuming uploads and reindexing; returns one page, newest first.

**Parameters**

| Name                   | Type                                                                                                                                                                                                                                      | Default | Description                                                                                                  |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------ |
| `page`                 | `integer`                                                                                                                                                                                                                                 | `1`     | Page number, starting at 1.                                                                                  |
| `page_size`            | `integer`                                                                                                                                                                                                                                 | `25`    | Results per page, up to 100.                                                                                 |
| `status`               | `PENDING \| STARTED \| SUCCESS \| FAILURE \| RETRY \| REVOKED \| null`                                                                                                                                                                    | `null`  | Keep tasks in this state.                                                                                    |
| `task_type`            | `consume_file \| train_classifier \| sanity_check \| index_optimize \| mail_fetch \| llm_index \| empty_trash \| check_workflows \| bulk_update \| reprocess_document \| build_share_link \| bulk_delete \| apply_ai_suggestions \| null` | `null`  | Keep tasks of this kind; `bulk_update` is the reindex that `bulk_edit_documents`' metadata operations start. |
| `acknowledged`         | `boolean \| null`                                                                                                                                                                                                                         | `null`  | Keep only acknowledged (true) or unacknowledged (false) tasks.                                               |
| `include_acknowledged` | `boolean`                                                                                                                                                                                                                                 | `false` | Also list tasks already acknowledged; by default only unacknowledged ones are listed.                        |

**Returns**

`object`

## `get_task`

**Get Background Task.** Read-only. Idempotent. Reaches outside the server.

Get one background task by id, with its status and result; returns null if there is none.

**Parameters**

| Name        | Type     | Default  | Description                                                          |
| ----------- | -------- | -------- | -------------------------------------------------------------------- |
| `task_uuid` | `string` | required | Task id, as returned by `upload_document` or listed by `list_tasks`. |

**Returns**

`object | null`

## `wait_for_task`

**Wait for Task to Finish.** Read-only. Idempotent. Reaches outside the server.

Wait for a background task to finish; returns the task with its final status and result.

**Parameters**

| Name              | Type     | Default  | Description                                                          |
| ----------------- | -------- | -------- | -------------------------------------------------------------------- |
| `task_uuid`       | `string` | required | Task id, as returned by `upload_document` or listed by `list_tasks`. |
| `timeout_seconds` | `number` | `60.0`   | Longest time to wait, up to 600 seconds.                             |

**Returns**

`object`
