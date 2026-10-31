# Claude Code

Claude Code can start the server for you, as Claude Desktop does. It can also connect to a server that already runs somewhere else. Started locally, the server runs with your user account's access and trusts the Claude Code session that started it; the [security model](https://pvliesdonk.github.io/paperless-mcp/unstable/security-model/index.md) says what that reaches.

## The plugin

The shortest route. In a Claude Code session, run:

```
/plugin marketplace add pvliesdonk/claude-plugins
/plugin install paperless-mcp@pvliesdonk
```

The first command registers the `pvliesdonk` marketplace, once. The second opens the plugin's details and asks for a scope:

- **user**: you, in every project on this machine;
- **project**: everyone who works in this repository;
- **local**: you, in this repository only.

The plugin follows stable releases and runs the released package with `uvx` at the version it was published with. Install `uv` first; the machine also needs network access the first time the server starts.

Run `/mcp` to see the server connected. To update or remove the plugin later, open `/plugin`, select it under **Installed**, and choose **Update now** or **Uninstall**; from a shell, `claude plugin update paperless-mcp@pvliesdonk` does the update.

From a shell, without a session (a setup script, say):

```
claude plugin marketplace add pvliesdonk/claude-plugins
claude plugin install paperless-mcp@pvliesdonk
```

The shell form installs at user scope unless `--scope project` or `--scope local` says otherwise, and the plugin loads when Claude Code next starts.

## The command

Without the plugin, install the server as a command, then register it with Claude Code:

```
uv tool install "pvliesdonk-paperless-mcp"
claude mcp add --transport stdio paperless-mcp -- paperless-mcp serve
```

Claude Code runs whatever follows the `--`, so settings for the server go on the command line as environment variables: `--env NAME=value` before the server's name, one per variable, from the [configuration reference](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/configuration/index.md). The entry is stored for the current project; `--scope user` makes it available in every project. `/mcp` shows it connected.

## A server that already runs

When someone runs the server for you over HTTP, register its URL instead:

```
claude mcp add --transport http paperless-mcp https://mcp.example.com/mcp
```

With a bearer token, add `--header "Authorization: Bearer <token>"`. Which credential the server wants is up to whoever runs it; [A remote server](https://pvliesdonk.github.io/paperless-mcp/unstable/get-started/http-client/index.md) covers both kinds.

## Ask Claude one question

> Which version of Paperless MCP is running?

Claude calls the server's `get_server_info` tool, which reads the server's version and the protocol revision in use and changes nothing. Then the first task below.

### Your first task

The command form needs the Paperless instance and a token as environment variables:

```
claude mcp add --transport stdio paperless-mcp \
  --env PAPERLESS_MCP_PAPERLESS_URL=https://paperless.example.com \
  --env PAPERLESS_MCP_API_TOKEN=your-paperless-api-token \
  -- paperless-mcp serve
```

Then a task that only reads:

> List the five documents most recently added to Paperless.

## Next

- [Claude Desktop](https://pvliesdonk.github.io/paperless-mcp/unstable/get-started/claude-desktop/index.md): the same server in the desktop app.
- [Installation](https://pvliesdonk.github.io/paperless-mcp/unstable/get-started/installation/index.md): the other ways to install it.
- [Use](https://pvliesdonk.github.io/paperless-mcp/unstable/use/index.md): what the server does for real tasks.
