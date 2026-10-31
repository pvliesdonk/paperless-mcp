# Server info

## `get_server_info`

**Server Info.** Read-only.

Report the version information of paperless-mcp; returns `server_name`, `server_version`, `core_version`, the MCP protocol revisions supported and the revision and client of this connection, and, when configured, the upstream service's version. Use it when asked which version or build is running or which protocol revision is in use.

**Parameters**

None.

**Returns**

`object`

The `paperless` block carries the version installed on the connected instance:

```
{
  "server_name": "paperless-mcp",
  "server_version": "1.0.2",
  "core_version": "7.2.0",
  "paperless": {"version": "2.14.7"}
}
```

When Paperless can't answer, the block is `{"version": null}` and the rest of the response is unaffected. That happens when Paperless is down, the URL is wrong or the token is rejected. It also happens when the token's Paperless user lacks the "view" permission on UI settings, which is where Paperless publishes its version. Nothing else this server does needs that permission.
