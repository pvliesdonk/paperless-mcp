# Configuration

Paperless MCP reads all configuration from environment variables. Domain variables carry the `PAPERLESS_MCP_` prefix; a few third-party variables (`FASTMCP_*`, `PUID`/`PGID`) keep their upstream names.

This page is the complete reference: every variable the server reads appears in exactly one table below. The tables come from the same source as `.env.example`, the packaged env files, and the [configuration generator](https://pvliesdonk.github.io/paperless-mcp/unstable/configuration-generator/index.md), so the four cannot disagree. The README carries a hand-picked subset of these variables as its quick entry point.

## Server

Transport, identity, and tool visibility. `PAPERLESS_MCP_SERVER_NAME` identifies the deployment, `PAPERLESS_MCP_INSTANCE_DESCRIPTION` distinguishes its material or responsibility for routing, and `PAPERLESS_MCP_INSTRUCTIONS_EXTRA` supplies deployment-specific behavioral policy. The legacy `PAPERLESS_MCP_INSTRUCTIONS` replaces all generated text, ignores both additive variables, and logs a deprecation warning at startup.

Generated guidance targets 1,536 UTF-16 units, reserving 512 units for normal operator routing and policy within Claude Code's known 2,048-unit limit. Crossing either threshold logs a warning; startup continues and the server does not truncate the instructions.

The generated guidance names the Paperless instance this deployment fronts, taking the URL from `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` or, unset, from `PAPERLESS_MCP_PAPERLESS_URL`. A model can then recognise a link to that instance and read the document id out of it.

`PAPERLESS_MCP_TOOLS_ALLOW` and `PAPERLESS_MCP_TOOLS_DENY` trim which tools an instance exposes. Hidden tools disappear from `tools/list` and are rejected on `tools/call`; resources and prompts are unaffected. Setting both variables, or setting one to a value with no names in it, is a startup error. A name matching no registered tool is ignored, but an allowlist that matches nothing logs a startup warning, since the instance then exposes zero tools. See `fastmcp-pvl-core`'s README for the full semantics.

`PAPERLESS_MCP_HEALTH_DETAIL` decides how much the unauthenticated `/health` and `/health/ready` bodies say, since anyone who can reach the port can read them: `status` alone, the default `standard` with the server name, version and a verdict per readiness check, or `full` with a redacted reason for each check that raised. See [Docker deployment](https://pvliesdonk.github.io/paperless-mcp/unstable/deployment/docker/#health) for the routes themselves.

| Variable                             | Default     | Description                                                                                                                                                                                                                                                 |
| ------------------------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_TRANSPORT`            | `stdio`     | Transport the server speaks: `stdio` for local Claude Desktop/Code, `http` or `sse` for a network server.                                                                                                                                                   |
| `PAPERLESS_MCP_HOST`                 | `127.0.0.1` | Interface the HTTP server binds to.                                                                                                                                                                                                                         |
| `PAPERLESS_MCP_PORT`                 | `8000`      | TCP port for the HTTP server.                                                                                                                                                                                                                               |
| `PAPERLESS_MCP_BASE_URL`             | (none)      | Public base URL of the deployed server (`https://mcp.example.com`). Required for OIDC. Also the fallback source of the MCP Apps domain when `app_domain` is unset.                                                                                          |
| `PAPERLESS_MCP_TOOLS_ALLOW`          | (none)      | Comma-separated explicit tool names this instance exposes; every other tool is hidden from listings and cannot be invoked. Names matching no registered tool are inert. Mutually exclusive with `tools_deny`. Takes effect through `apply_tool_visibility`. |
| `PAPERLESS_MCP_TOOLS_DENY`           | (none)      | Comma-separated explicit tool names hidden from this instance (absent from listings, cannot be invoked). Names matching no registered tool are inert. Mutually exclusive with `tools_allow`. Takes effect through `apply_tool_visibility`.                  |
| `PAPERLESS_MCP_SERVER_NAME`          | (none)      | Rename this server instance; defaults to the project name.                                                                                                                                                                                                  |
| `PAPERLESS_MCP_INSTANCE_DESCRIPTION` | (none)      | Concise routing context that distinguishes this deployment's material or responsibility.                                                                                                                                                                    |
| `PAPERLESS_MCP_INSTRUCTIONS_EXTRA`   | (none)      | Deployment-specific behavioral policy added to the generated MCP instructions.                                                                                                                                                                              |
| `PAPERLESS_MCP_INSTRUCTIONS`         | (none)      | Legacy: replaces all generated MCP instructions (deprecated; use \_INSTANCE_DESCRIPTION for routing and \_INSTRUCTIONS_EXTRA for policy).                                                                                                                   |
| `PAPERLESS_MCP_HTTP_PATH`            | `/mcp`      | Mount path for the MCP endpoint; the health routes derive their prefix from it.                                                                                                                                                                             |
| `PAPERLESS_MCP_HEALTH_DETAIL`        | `standard`  | How much the unauthenticated /health and /health/ready bodies say: status, standard (adds name, version and per-check verdicts), or full (adds redacted reasons; trusted networks only).                                                                    |

## Authentication

Callers authenticate with a bearer token, with OIDC, or with both. OIDC itself has two modes. **remote** validates tokens locally against the provider's JWKS and needs only `PAPERLESS_MCP_BASE_URL` and `PAPERLESS_MCP_OIDC_CONFIG_URL`. **oidc-proxy** runs the OAuth flow itself and also needs `PAPERLESS_MCP_OIDC_CLIENT_ID` and `PAPERLESS_MCP_OIDC_CLIENT_SECRET`, registered with the provider as a confidential client whose redirect URI points at this server.

The Required column below marks the oidc-proxy set. Setting all four selects that mode and omitting the two client credentials selects remote, so `PAPERLESS_MCP_AUTH_MODE` is the way to state the choice rather than leave it to be inferred. With none of these set, the server starts and serves unauthenticated. See the [authentication guide](https://pvliesdonk.github.io/paperless-mcp/unstable/guides/authentication/index.md) for setup, mapped multi-subject tokens, and troubleshooting.

| Variable                                 | Default                 | Required | Description                                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------------------- | ----------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_BEARER_TOKEN`             | (none)                  | No       | Single shared bearer token; enables bearer auth unless `bearer_tokens_file` is set, which takes precedence.                                                                                                                                                                                                                                                                   |
| `PAPERLESS_MCP_OIDC_CONFIG_URL`          | (none)                  | **Yes**  | OIDC discovery document URL (`https://auth.example.com/.well-known/openid-configuration`).                                                                                                                                                                                                                                                                                    |
| `PAPERLESS_MCP_OIDC_CLIENT_ID`           | (none)                  | **Yes**  | OIDC client identifier registered with the provider.                                                                                                                                                                                                                                                                                                                          |
| `PAPERLESS_MCP_OIDC_CLIENT_SECRET`       | (none)                  | **Yes**  | OIDC client secret registered with the provider.                                                                                                                                                                                                                                                                                                                              |
| `PAPERLESS_MCP_OIDC_AUDIENCE`            | (none)                  | No       | Expected `aud` claim; tokens issued for another audience are rejected.                                                                                                                                                                                                                                                                                                        |
| `PAPERLESS_MCP_OIDC_REQUIRED_SCOPES`     | `openid`                | No       | Scopes a caller must present, space- or comma-separated. Defaults to `openid` in oidc-proxy mode.                                                                                                                                                                                                                                                                             |
| `PAPERLESS_MCP_OIDC_ADVERTISED_SCOPES`   | `openid offline_access` | No       | Scopes advertised to MCP clients in protected-resource metadata, space- or comma-separated. Overrides the default `openid offline_access`; `oidc_required_scopes` is always added on top. Set this when the registered client is not permitted `offline_access`, or to have clients request extra claim scopes (such as `groups`) without also requiring them in every token. |
| `PAPERLESS_MCP_OIDC_JWT_SIGNING_KEY`     | `derived`               | No       | Signing key for issued tokens; used in oidc-proxy mode only. When unset, the key is derived deterministically from `oidc_client_secret`, so tokens survive a restart. Rotating that secret then invalidates every issued token. Set this explicitly to decouple token validity from secret rotation. Generate with `openssl rand -hex 32`.                                    |
| `PAPERLESS_MCP_OIDC_VERIFY_ACCESS_TOKEN` | `false`                 | No       | Validate the access token instead of the id token.                                                                                                                                                                                                                                                                                                                            |
| `PAPERLESS_MCP_AUTH_MODE`                | (none)                  | No       | Explicit auth-mode override, accepting `remote` or `oidc-proxy` (case- and whitespace-insensitive). When unset the mode is auto-detected from which auth variables are set; the override exists because having all four OIDC variables set is ambiguous between those two modes. Other values are ignored with a warning.                                                     |
| `PAPERLESS_MCP_BEARER_TOKENS_FILE`       | (none)                  | No       | Path to a TOML file mapping bearer tokens to subjects; overrides the single-token `bearer_token` mode.                                                                                                                                                                                                                                                                        |
| `PAPERLESS_MCP_BEARER_DEFAULT_SUBJECT`   | `bearer-anon`           | No       | Subject assigned to the single-token bearer mode; ignored when `bearer_tokens_file` is set, since mapped mode carries per-token subjects.                                                                                                                                                                                                                                     |

## Persistence

One URL configures every stateful subsystem. A `redis://` `PAPERLESS_MCP_KV_STORE_URL` is also reused for background tasks when `PAPERLESS_MCP_TASKS_URL` is unset, so a single URL covers both.

| Variable                        | Default              | Description                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_KV_STORE_URL`    | `file:///data/state` | Persistent-state backend URL shared by every pvl-core subsystem that needs state. `memory://` is in-process and lost on restart; `file:///path` persists on one server; `redis://`, `dynamodb://` and `mongodb://` each need their matching extra. When unset, defaults to `file:///data/state` (the volume family Docker images mount), or to `memory://` (with a warning) on a host where that directory is not usable. |
| `PAPERLESS_MCP_EVENT_STORE_URL` | (none)               | Legacy state-backend override, used by `build_event_store` and `build_kv_store` only when `kv_store_url` is unset. It then backs every namespace, not just HTTP resumability. Prefer `kv_store_url` for new deployments.                                                                                                                                                                                                  |
| `PAPERLESS_MCP_TASKS_URL`       | (none)               | Background-task (Docket) backend URL: `memory://` is in-process and lost on restart; `redis://` is durable and multi-process. When unset, a `redis://` `kv_store_url` is reused for tasks too; otherwise fastmcp's `memory://` default applies. Only applies when task-enabled tools exist. Applied via `configure_task_backend`.                                                                                         |

## Background tasks

Every Paperless MCP instance wires a background-task backend at startup, so a tool registered with `task=True` works with no extra setup. `PAPERLESS_MCP_TASKS_URL` (under Persistence above) picks the backend: `memory://` runs tasks in-process and loses them on restart; `redis://...` is durable and shared across processes. With neither it nor a `redis://` KV store set, the backend falls back to `memory://`, which the server logs at startup when running over HTTP. The queue name comes from the `PAPERLESS_MCP` prefix, so two servers sharing one Redis do not share a queue.

Worker tuning stays on the native `FASTMCP_DOCKET_*` variables below. Set the backend through `PAPERLESS_MCP_TASKS_URL` rather than `FASTMCP_DOCKET_URL`: the former wins when both are set, and the server warns about the disagreement.

| Variable                                | Default | Description                                                                              |
| --------------------------------------- | ------- | ---------------------------------------------------------------------------------------- |
| `FASTMCP_DOCKET_CONCURRENCY`            | `10`    | Maximum background tasks this worker runs at once.                                       |
| `FASTMCP_DOCKET_WORKER_NAME`            | (none)  | Identifies this worker in the queue; defaults to a generated name.                       |
| `FASTMCP_DOCKET_REDELIVERY_TIMEOUT`     | `300`   | Seconds before a task claimed by a worker that never finished is redelivered to another. |
| `FASTMCP_DOCKET_RECONNECTION_DELAY`     | `5`     | Seconds to wait before reconnecting after the queue connection drops.                    |
| `FASTMCP_DOCKET_MINIMUM_CHECK_INTERVAL` | `0.05`  | Seconds between queue polls; lower cuts latency and raises idle load.                    |

## MCP Apps

| Variable                   | Default | Description                                                                                  |
| -------------------------- | ------- | -------------------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_APP_DOMAIN` | (none)  | MCP Apps iframe domain, used for CSP sandboxing. Overrides the host derived from `base_url`. |

## Logging

`FASTMCP_ENABLE_RICH_LOGGING` picks the shape of FastMCP's own log output, the request-logging middleware included. Left on, Rich renders each record with color, a time column and the source file that emitted it. Turned off, the middleware emits one JSON object per record and the rest of FastMCP's loggers emit `LEVEL: message`. This server's own `paperless_mcp.*` lines are not affected either way: the CLI attaches its own one-line handler to the root logger.

The container image and the packaged systemd unit both default it to `false`, because neither stream is a terminal. Rich falls back to 80 columns there, and a structured record does not fit in what its own columns leave, so each record wraps across three space-padded lines that neither `docker logs` nor a collector reads back. `docker logs -t` and `journalctl` both carry a timestamp per line, covering the column Rich stops printing. Both are ordinary environment defaults: `.env`, the compose `environment:` block and `/etc/paperless-mcp/env` all override them. Turning Rich back on inside a container wraps the records again unless `COLUMNS` is set too, which is what Rich reads in preference to asking the terminal.

| Variable                      | Default | Description                                                                                                                                                                                                                 |
| ----------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FASTMCP_LOG_LEVEL`           | `INFO`  | Log level for FastMCP internals and app loggers (DEBUG / INFO / WARNING / ERROR / CRITICAL). The -v CLI flag overrides to DEBUG.                                                                                            |
| `FASTMCP_ENABLE_RICH_LOGGING` | `true`  | Rich color output for a terminal; false gives one plain or JSON line per record. Off in the container image and the systemd unit, since neither is a terminal and Rich wraps a structured record at its 80-column fallback. |

## Container runtime

Read by the container entrypoint (Docker / Compose), not by the server process.

| Variable | Default | Description                                                                                                  |
| -------- | ------- | ------------------------------------------------------------------------------------------------------------ |
| `PUID`   | `1000`  | Run the server process as this UID; the container entrypoint reassigns ownership of writable paths to match. |
| `PGID`   | `1000`  | Run the server process as this GID; pair with PUID to match the owner of a mounted volume.                   |

## Remote debugger

Development only; the image must be built with `--build-arg DEBUG=true`, and the protocol is unauthenticated. See [remote debugging](https://pvliesdonk.github.io/paperless-mcp/unstable/deployment/docker/#remote-debugging).

| Variable                   | Default | Description                                                                 |
| -------------------------- | ------- | --------------------------------------------------------------------------- |
| `PAPERLESS_MCP_DEBUG_PORT` | `5678`  | debugpy listen port; the image must be built with `--build-arg DEBUG=true`. |
| `PAPERLESS_MCP_DEBUG_WAIT` | `false` | Block startup until a debugger attaches.                                    |

## Domain variables

`PAPERLESS_MCP_PAPERLESS_URL` and `PAPERLESS_MCP_API_TOKEN` are the two variables the server cannot start without: leave either unset and startup stops with a message naming it. The table below still shows them under `Required: No`, because that column reports whether the underlying field declares a default rather than whether the server runs without a value; read the description column for these two. `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` lets you name a different base URL for user-visible links than the internal API URL the server calls; unset, it defaults to `PAPERLESS_MCP_PAPERLESS_URL`, and trailing slashes are stripped from both.

A minimal `.env`:

```
PAPERLESS_MCP_PAPERLESS_URL=http://paperless.local:8000
PAPERLESS_MCP_API_TOKEN=abc123yourtokenhere
PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS=60
PAPERLESS_MCP_DEFAULT_PAGE_SIZE=50
```

### Paperless

| Variable                             | Default | Required | Description                                                                                               |
| ------------------------------------ | ------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `PAPERLESS_MCP_PAPERLESS_URL`        | (none)  | No       | Base URL of the Paperless-NGX REST API, without a trailing slash. The server refuses to start without it. |
| `PAPERLESS_MCP_API_TOKEN`            | (none)  | No       | Paperless service-account token used for outbound API requests. The server refuses to start without it.   |
| `PAPERLESS_MCP_HTTP_TIMEOUT_SECONDS` | `30.0`  | No       | Per-request HTTP timeout in seconds.                                                                      |
| `PAPERLESS_MCP_HTTP_RETRIES`         | `2`     | No       | Retries for idempotent requests after network errors or 5xx responses.                                    |
| `PAPERLESS_MCP_DEFAULT_PAGE_SIZE`    | `25`    | No       | Default page size for list tools, from 1 through 100.                                                     |
| `PAPERLESS_MCP_PAPERLESS_PUBLIC_URL` | (none)  | No       | Public Paperless UI URL for user-visible links; defaults to PAPERLESS_URL.                                |
