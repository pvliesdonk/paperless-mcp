# System

Two tools report a Paperless version, and they answer different questions:

| Question                                          | Tool                                                                                                                  | Example answer                      |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Which Paperless is this server connected to?      | [`get_server_info`](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/tools/server_info/#get_server_info) | `2.14.7`                            |
| Is there a newer Paperless release to upgrade to? | `get_remote_version`                                                                                                  | `2.20.14`, `update_available: true` |

## `get_statistics`

**Get Paperless Statistics.** Read-only. Idempotent. Reaches outside the server.

Get counts for the whole archive: documents, inbox documents, tags, correspondents, types, characters and file types.

**Parameters**

None.

**Returns**

`object`

## `get_remote_version`

**Check for Paperless Updates.** Read-only. Idempotent. Reaches outside the server.

Check whether a newer Paperless-NGX release exists; returns the newest release.

That is the newest release published upstream, not the version installed on this instance, with a flag saying whether it is newer. Use `get_server_info` for the installed version.

**Parameters**

None.

**Returns**

`object`
