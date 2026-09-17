---
type: Reference
title: Who may read an MCP resource
description: Why a resource URI is not something the model can call, which party issues resources/read, and how far hosts differ on giving the model a path to one.
subject_version: "MCP specification 2025-06-18"
valid_for: "MCP 2025-06-18 and later revisions that keep resources application-driven"
generated:
  by: process:researching-references
  at: 2026-09-17
stale_after: 2027-03-17
status: stable
verified:
  - by: process:researching-references
    at: 2026-09-17
sources:
  - id: mcp-resources
    title: Model Context Protocol — Resources (2025-06-18)
    resource: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
    accessed: 2026-09-17
  - id: fastmcp-rat
    title: FastMCP — Resources as Tools transform
    resource: https://gofastmcp.com/servers/transforms/resources-as-tools
    accessed: 2026-09-17
  - id: claude-code-mcp
    title: Claude Code — MCP documentation
    resource: https://code.claude.com/docs/en/mcp
    accessed: 2026-09-17
---

# Who may read an MCP resource

Written because this server's composed instructions told the model to "read
`paperless://documents/<id>`", which is not an action the model has
([#114](https://github.com/pvliesdonk/paperless-mcp/issues/114) review). The
question generalises: any instruction prose, tool description or prompt that
points the model at a resource URI depends on this behaviour.

## The protocol never makes the model the actor

`resources/read` is a **client to server** request. The specification's message
flow shows only `Client->>Server: resources/read`; there is no message a model
emits and no server-side entry point the model reaches directly. The model's
only protocol-level action is a tool call. [source: mcp-resources]

The interaction model is explicit that the decision is the host's:

> Resources in MCP are designed to be **application-driven**, with host
> applications determining how to incorporate context based on their needs.

[source: mcp-resources]

## But the host may route the model's choice

The same section lists, as one of three example patterns a host may implement:

> Implement automatic context inclusion, based on heuristics or the AI model's
> selection

[source: mcp-resources]

So a model-selected resource read is **permitted and optional**, never
guaranteed. The spec adds that "implementations are free to expose resources
through any interface pattern that suits their needs — the protocol itself does
not mandate any specific user interaction model." [source: mcp-resources]

Three host positions therefore all conform:

| Host behaviour | Effect on prose naming a resource URI |
|---|---|
| User picks resources in the UI (picker, `@` mention) | The model cannot act on the URI; the instruction is dead weight |
| Host exposes resource reads to the model as tools | The model can act on it, via the host's tool, not the server's |
| Client has no resource support at all | The URI is unreachable by any party |

The third row is not hypothetical. FastMCP ships a `ResourcesAsTools` transform
whose stated reason is that "Some MCP clients only support tools. They cannot
list or read resources directly because they lack resource protocol support."
It generates `list_resources` and `read_resource` **tools** precisely so that
tool-only clients can reach resources. [source: fastmcp-rat]

## Claude Code, the host this project is developed against

Claude Code sits in the second row: it provides `ListMcpResourcesTool` and
`ReadMcpResourceTool(server, uri)` in the model's own tool surface, so a model
running there can read `paperless://documents/42` by calling a host tool.

[verified: observed 2026-09-17 — both tool schemas were loaded and read
in-session from the running Claude Code host, `ReadMcpResourceTool` taking
`server` and `uri` and described as "Reads a specific resource from an MCP
server".] The published Claude Code MCP page documents server configuration,
tool discovery and auth, and does **not** describe the resource interaction
model, so the in-session schema is the stronger evidence and is what this claim
rests on. [source: claude-code-mcp]

This is the trap for anyone testing instruction prose here: resource-reading
prose *appears* to work, because this host happens to grant the affordance the
protocol does not require.

## Consequence for instruction prose

1. Never phrase a resource URI as something the model does. "Read
   `scheme://thing`" is false on a conforming host that has no such affordance.
2. Name a **tool** for anything the model must be able to do unaided.
3. A resource URI is still worth stating — a host with a picker, or a model on
   a host like Claude Code, can use it — but frame it as what the *client*
   reads, so a model without the affordance does not treat the failure as its
   own.

## What this server publishes, and where the two surfaces disagree

Six of the eight `paperless://documents/{id}` variants have a tool twin:

| Resource | Tool |
|---|---|
| `paperless://documents/{id}` | `get_document` |
| `.../content` | `get_document_content` |
| `.../metadata` | `get_document_metadata` |
| `.../notes` | `get_document_notes` |
| `.../history` | `get_document_history` |
| `.../thumbnail` | `get_document_thumbnail` |
| `.../preview` | **none** |
| `.../download` | **none** |

`/preview` and `/download` are resource-only, so on a tool-only client no party
can reach them through the model at all. That gap is a fact about this server's
surface, not about MCP, and it is the reason the instruction snippet names it
rather than implying the eight are interchangeable.

Collection resources (`tags://paperless`, `config://paperless`, and the rest)
all have `list_*` or `get_*` tool twins.
