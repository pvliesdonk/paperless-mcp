# 2.0

Paperless MCP moves onto the current shared platform, three template majors and three library majors ahead of where it was. Operators get unauthenticated liveness and readiness routes, a `compose.yml` that runs as shipped, container logs a machine can parse, and two new variables for shaping the server's instructions without replacing them wholesale. `get_server_info` now also reports the Paperless-NGX version installed on the instance it is connected to. Several deployment defaults changed in ways that need action, so read [Upgrading](#upgrading) before you deploy this one.

## A current platform underneath

The server carried its shared runtime from `fastmcp-pvl-core` 4.11.3 to 7.2.0 and its project template from v5.6.3 to v8.2.0, in one step rather than in stages ([#102](https://github.com/pvliesdonk/paperless-mcp/issues/102), [#108](https://github.com/pvliesdonk/paperless-mcp/pull/108)). The motivation was not the dependency itself. As [#102](https://github.com/pvliesdonk/paperless-mcp/issues/102) put it, the weekly update bot "advances one major at a time and opens a v6 pull request first, and the same `server.py` and README hunks re-conflict at each step." Taking the jump whole produced "one conflicted file instead of seven."

Three things that upgrade unlocks are visible to anyone running the server.

### Liveness and readiness routes

Under the HTTP transport the server now answers `GET /health` (a static 200 for as long as the process serves) and `GET /health/ready` (503 when a backing check fails). One check ships today, covering the key-value store.

Both routes sit outside the MCP mount, which is also what makes them unauthenticated: they answer normally while the MCP endpoint still returns `401`. Treat that as a posture change. A deployment that was fully authenticated on its published port now serves two endpoints that are not, and at the default detail level their bodies disclose the server name and version.

`PAPERLESS_MCP_HEALTH_DETAIL` controls how much they say. `status` returns the status alone; the default `standard` adds the server name and version on `/health` and a verdict per check on `/health/ready`; `full` adds a redacted reason for each check that raised and belongs only where the port is reachable from a trusted network. The shipped `compose.yml` and the image's own `HEALTHCHECK` both probe `/health` rather than `/health/ready`, deliberately, because restarting a container does not fix an unreachable backing store.

The route prefix follows the mount: `PAPERLESS_MCP_HTTP_PATH` has a trailing `mcp` segment stripped, so the default `/mcp` gives `/health`, and a mount at `/paperless-mcp/mcp` gives `/paperless-mcp/health`. The shipped probes assume the default, so a non-default mount means moving both by hand. See [Docker deployment](https://pvliesdonk.github.io/paperless-mcp/2.1/deployment/docker/index.md) for the probe configuration.

### Instructions you can shape instead of replace

Two new variables let an operator add to the generated MCP instructions rather than overwrite them. `PAPERLESS_MCP_INSTANCE_DESCRIPTION` carries concise routing context that distinguishes this deployment from another one a client may also have mounted. `PAPERLESS_MCP_INSTRUCTIONS_EXTRA` carries deployment-specific behavioural policy, appended to the generated text. Neither has a default; both are documented in [Configuration](https://pvliesdonk.github.io/paperless-mcp/2.1/configuration/index.md).

The older `PAPERLESS_MCP_INSTRUCTIONS` still works and still replaces all generated text, but it is now deprecated, logs a warning at startup, and silently ignores both additive variables when it is set. If you set it only to append a sentence, the two variables above are what you actually wanted.

Generated guidance targets 1,536 UTF-16 units, reserving 512 units for operator routing and policy inside Claude Code's 2,048-unit limit. Going over warns; it never truncates and never fails startup.

### A compose file that runs

The shipped `compose.yml` used to be a reverse-proxy stub that built from the checkout. It now pulls the published image and starts as a quick start: copy `.env.example` to `.env` and run `docker compose up -d`. It publishes port 8000, tolerates a missing `.env`, and carries a health probe.

The Traefik labels it used to ship are gone, and that is a breaking change for anyone who built on them. See [Upgrading](#upgrading).

## Knowing which Paperless you are talking to

`get_server_info` already reported this server's own build. It now also reports the Paperless-NGX version installed on the instance it is connected to, in the same call ([#117](https://github.com/pvliesdonk/paperless-mcp/issues/117), [#121](https://github.com/pvliesdonk/paperless-mcp/pull/121)). The motivating report, quoted in [#40](https://github.com/pvliesdonk/paperless-mcp/issues/40) from a client validation write-up, describes the situation exactly:

> When debugging "is the latest fix deployed?" (exactly the situation we hit ten minutes ago when a pull-without-rebuild left v0.x running), having a one-call sanity check would help.

The response gains a `paperless` block:

```
{
  "server_name": "paperless-mcp",
  "server_version": "1.0.2",
  "core_version": "7.2.0",
  "paperless": {"version": "2.14.7"}
}
```

That block carries identity only, and deliberately holds no `update_available` key: mixing identity with an update check into one field is what produced the labelling bug described below, so the update question stays with `get_remote_version`.

Nothing needs enabling. The version is read from the Paperless UI settings endpoint, reusing the connection the server already holds, and costs one extra request per call.

**It does cost one permission.** The endpoint that publishes the installed version is gated on a model permission, so the token's Paperless user needs the view permission on UI settings. A narrow service account without it gets a `403`. That degrades to `{"version": null}` rather than failing the call, because the version is optional enrichment of a tool whose real job is reporting this server's build. Note that `{"version": null}` is also what you get when Paperless is down, when the URL is wrong, and when the token is rejected, so a null here means "could not ask," not "no version." Granting the permission is the fix if you want it populated; everything else the server does is unaffected either way. [Tools](https://pvliesdonk.github.io/paperless-mcp/2.1/tools/index.md) documents the full shape.

### `get_remote_version` now says which question it answers

`get_remote_version` reports the newest Paperless-NGX release published on GitHub, and whether that is newer than the connected instance. It never reported the version the instance runs. Its description said "Fetch Paperless version info," and the matching resource said it returned "the remote Paperless-NGX version," which reads as the identity of the instance you are connected to ([#123](https://github.com/pvliesdonk/paperless-mcp/issues/123), [#127](https://github.com/pvliesdonk/paperless-mcp/pull/127)).

The wording was wrong in a way that hid itself: the two answers coincide while an instance is up to date, and diverge exactly when an update is pending. The tool, the `remote-version://paperless` resource and both documentation tables now say which question each answers and point at `get_server_info` for the installed version.

The behaviour did not change. The tool calls the same endpoint and returns the same fields; only the descriptions changed, so no client needs updating. A dated reference recording what each of the three Paperless version endpoints reports, and what each costs in permissions, now ships in the repository for whoever next has to reason about this.

## A read-only switch that never worked is gone

`PAPERLESS_MCP_READ_ONLY` was documented in the README and in the example compose file as a way to disable every mutating tool at startup. No code ever read it, in any released version. As [#101](https://github.com/pvliesdonk/paperless-mcp/issues/101) puts it, "an operator who sets `PAPERLESS_MCP_READ_ONLY=true` today gets a fully writable server and no warning."

The documentation for it is gone ([#104](https://github.com/pvliesdonk/paperless-mcp/pull/104)), and the `config://paperless` resource no longer reports a `read_only` key that was always false.

Nothing stops working, because nothing ever worked. But if you set that variable believing it protected your archive, it did not, and it has not in any version you could have installed. `PAPERLESS_MCP_TOOLS_ALLOW` and `PAPERLESS_MCP_TOOLS_DENY` are the supported way to restrict the tool surface, and they do work.

## The tool reference now matches the server

The published tool reference documented 38 of the 49 registered tools. Eleven that the server had always exposed, including `upload_document`, `get_document_thumbnail`, `get_document_suggestions` and both remaining bulk-edit tools, were missing from it. The table also listed a `create_document` tool that has never existed; the real tool for that job is `upload_document`, and it was one of the undocumented eleven.

All 49 are now listed, the invented row is gone, and the MCP resources have a reference page of their own for the first time. No tool or resource was added, removed or renamed in this release: the server's surface is the same 49 tools and 18 resources it was before, and only the description of it changed.

## Upgrading

This release changes deployment defaults. The MCP tool and resource surface is unchanged, and nothing importable from `paperless_mcp` changed, so clients and any downstream Python consumer are unaffected.

**Refresh the lock file before you build.** A stale lock file builds an image that fails at import time, because the image installs from the lock with `--frozen`.

**If you used the shipped Traefik labels.** `compose.yml` no longer carries them and no longer builds from the checkout. The reverse-proxy configuration moved to an overlay you copy from [Docker deployment](https://pvliesdonk.github.io/paperless-mcp/2.1/deployment/docker/index.md). Worth knowing while you migrate: the labels never routed as shipped, because the file declared no network for Traefik to join.

**If you set `PAPERLESS_MCP_PORT` for a container.** The image now pins `--port 8000`, so that variable no longer moves the listener and no error is raised. A container started with `-e PAPERLESS_MCP_PORT=9000 -p 9000:9000` serves on 8000 behind a mapping pointing at a closed port. Change the host side instead, as in `-p 9000:8000`. Outside a container the variable still works.

**If you put a hostname in `PAPERLESS_MCP_HOST`.** It used to be interpolated into the Traefik router rule as a public name as well as being the bind address. Only the bind address remains, so a public FQDN left there now fails to start when it does not resolve to a local interface. This cannot affect the container, which pins its own host, but it does affect systemd and bare `serve` deployments.

**If you parse the logs.** The container image and the packaged systemd unit now disable Rich output, because neither stream is a terminal and Rich was wrapping each structured record across three lines at an assumed 80 columns. Anything matching the old layout, with its leading timestamp and trailing source location, matches nothing now. This is not a blanket switch to JSON: request-logging records become one JSON object per line, other library loggers become `LEVEL: message`, and this project's own log lines were always one line. To keep the old output in a container, set `FASTMCP_ENABLE_RICH_LOGGING=true` and `COLUMNS=200`.

One asymmetry is worth knowing: an existing `.deb` or `.rpm` install keeps the old Rich output. The package only creates `/etc/paperless-mcp/env` when it is absent, that file overrides the unit's own setting, and the older example enabled Rich. Fresh package installs and all container deployments get the new behaviour.

**If you run Docker Compose.** The shipped file needs Compose 2.24.0 or newer, and the reverse-proxy overlay needs 2.24.4 or newer. An older Compose fails to parse them.

**If you read the package description.** The text in `server.json`, on PyPI, in the MCP registry entry and on the Claude Code plugin manifest was shortened from 148 to 96 characters to fit a registry limit. The server behaves identically; only the advertised description changed.
