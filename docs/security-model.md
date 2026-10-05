---
description: "What the server protects, what it can reach, and what stays the operator's responsibility."
kind: explanation
---

# Security model

This page states what paperless-mcp protects and what it leaves to the operator. [Authentication](deploy/authentication.md) covers how to configure each mode, and `SECURITY.md` in the repository covers how to report a vulnerability.

## Authentication is the boundary

Over HTTP, authentication is the only access control: a bearer token, a mapped bearer token file, or OIDC. A request without a valid credential is refused before it reaches a tool. It is the same model as any other MCP server reached over HTTP.

With OIDC, which credentials the server accepts depends on the [mode](deploy/oidc.md#auth-modes):

- **`oidc-proxy`:** the server is the OAuth client registered with the identity provider and runs the sign-in itself. Anyone the provider lets sign in to that client gets through.
- **`remote`:** the server is a resource server. MCP clients get tokens from the provider on their own, and the server accepts any unexpired token the provider's issuer signed, unless `PAPERLESS_MCP_OIDC_AUDIENCE` or `PAPERLESS_MCP_OIDC_REQUIRED_SCOPES` narrows that down.

The server keeps no list of allowed users, so every caller it accepts has the full tool surface. Limit who can get a credential at the provider, and in `remote` mode set the audience.

## Running without authentication

With no authentication variables set, the server starts in mode `none` and logs `auth_mode_resolved` at warning level with `mode=none`. Every client that can open a connection to the port then has the full tool surface. Turning authentication off is a decision to trust everything that can reach the port.

The bind address decides which machines reach the port, and nothing more. Binding to `127.0.0.1` keeps other machines out. It does not keep out other processes on the host, nor a web page in a browser on the host that uses DNS rebinding. Without authentication, run the server only where everything that reaches the port is trusted, such as a single-user workstation or a private network you control.

## stdio

Over stdio there is no network listener and no authentication. The MCP client starts the server as a child process, and the server trusts that client. Authentication variables have no effect there, and the server logs `auth_configured_but_stdio_skips_enforcement` when they are set.

## What an authenticated caller can reach

An authenticated caller has every tool the instance exposes. Each tool runs with the server's own privileges: its filesystem and network access, and any credential in its configuration. `PAPERLESS_MCP_TOOLS_ALLOW` and `PAPERLESS_MCP_TOOLS_DENY` trim that set for an instance; see [Configuration](reference/configuration.md).

<!-- DOMAIN-SECURITY-MODEL-SURFACE-START — what THIS server's tools reach; kept across copier update -->
Every tool acts on one Paperless-NGX instance, the one at `PAPERLESS_MCP_PAPERLESS_URL`, and sends every request with the single API token in `PAPERLESS_MCP_API_TOKEN`. The tools make no other outbound requests; the server itself also connects to the OIDC provider in the OIDC modes, and to the network store a `PAPERLESS_MCP_KV_STORE_URL` or `PAPERLESS_MCP_TASKS_URL` names (Redis, DynamoDB or MongoDB). An authenticated caller acts as the Paperless user that owns that token, and the permissions Paperless grants that user are the only limit on what the tools can do:

- **Read** documents, their OCR text, thumbnails, file metadata, notes, history and suggestions, as well as tags, correspondents, document types, storage paths, custom fields, saved views, share links, tasks and instance statistics.
- **Change** document metadata, notes, tags, correspondents, document types and custom fields, one at a time or in bulk.
- **Delete** documents, notes, tags, correspondents, document types and custom fields.
- **Upload** new documents for Paperless to consume.

A service-account token with only the permissions the deployment needs is the way to narrow this set. Hiding the delete tools with `PAPERLESS_MCP_TOOLS_DENY` changes the tool list the model sees. The token's permissions stay the same.

Over HTTP with `PAPERLESS_MCP_BASE_URL` set, `create_download_link` and `create_upload_link` issue single-use links. A link needs no credential: whoever holds it can use it once, before it expires. The server re-checks the document against Paperless when a download link is redeemed.
<!-- DOMAIN-SECURITY-MODEL-SURFACE-END -->

## What answers without a credential

Some routes answer anyone who can reach the port, with authentication on or off:

- `/health` and `/health/ready`. `PAPERLESS_MCP_HEALTH_DETAIL` decides how much they say; see [Health](deploy/docker.md#health).
- In the OIDC modes, the OAuth metadata and sign-in routes a client uses before it holds a token.
- On a server with transfer links, `/transfer/{token}`. The token in the URL is the credential, good for one transfer of one file before it expires; [Transfer links](deploy/transfer-links.md) says what the server accepts on it.

## What the operator is responsible for

- **TLS.** The server speaks plain HTTP. Terminate TLS at a reverse proxy in front of it.
- **Exposure.** Which interfaces and networks can reach the port. [Ports](deploy/docker.md#ports) covers the published port of the Docker deployment.
- **Secrets.** Bearer tokens, OIDC client secrets and the credentials the tools use live in the environment or in files you control. Anyone who can read them can act as the server.
- **Token lifetimes.** Under OIDC, a leaked access or ID token stays usable until it expires, because the server checks expiry and signature but not revocation; a refresh token stays usable until it expires or you revoke it at the provider. The lifetimes you set on the provider are that exposure window; [Authentication](deploy/authentication.md#what-works-today) gives the trade-off.
- **The debugger port.** A debug build's debugger port grants code execution to anyone who reaches it; see [Remote debugging](deploy/docker.md#remote-debugging).

## Host and Origin validation

FastMCP can refuse requests whose `Host` or `Origin` header does not name the server, which blocks DNS rebinding against a server running without authentication. It is off by default, and the model above does not depend on it. To turn it on, set `FASTMCP_HTTP_HOST_ORIGIN_PROTECTION` to `auto`, which checks requests that reach the server on a local address, or to `true`, which checks every request against `FASTMCP_HTTP_ALLOWED_HOSTS` (a JSON list of host names). Behind a reverse proxy, test it before relying on it: a request whose headers do not match is refused.

## Reporting a vulnerability

Read this page before reporting. A finding that depends on authentication being off describes the configuration above rather than a flaw in the server. `SECURITY.md` covers the reporting channel, scope and response targets.

<!-- DOMAIN-SECURITY-MODEL-EXTRA-START -->
<!-- Project-specific security notes go here; kept across copier update. -->
<!-- DOMAIN-SECURITY-MODEL-EXTRA-END -->
