# Composed instructions

Internal design note. `AGENTS.md`'s "Key Design Decisions" carries the summary;
this page carries the argument.

## What the server says about itself

pvl-core composes `FastMCP.instructions` from role-tagged snippets rather than
templating one string. This project contributes three:

| Role | Contributor | Content |
|---|---|---|
| `IDENTITY` | `server.py`, shaped API | `paperless-mcp: <product description>` |
| `CAPABILITIES` | `domain.add_instance_instructions` | the instance URL and the URI families |
| `DOCUMENTATION` | `server.py`, shaped API | the `llms.txt` pointer |

The operator's `PAPERLESS_MCP_INSTANCE_DESCRIPTION` (`ROUTING`) and
`PAPERLESS_MCP_INSTRUCTIONS_EXTRA` (`POLICY`) are added by `finalize_instructions`
itself, not here.

Until [#114](https://github.com/pvliesdonk/paperless-mcp/issues/114) the middle
row did not exist, so the composed text never named the Paperless instance the
server fronts. A model handed `https://paperless.example.org/documents/42/` in
conversation had no stated basis for recognising it as this server's instance,
and nothing it reads before its first call described the `paperless://` resource
URIs at all.

## One snippet, not two

The instance URL on its own would suit the `INSTANCE` role, whose purpose is
exactly "enforced instance facts". It is nonetheless one `CAPABILITIES` snippet,
because the URL is only *useful* together with the mapping it enables: that a
link under it carries a document id, and that the id addresses a `paperless://`
resource. `_ROLE_ORDER` serialises `INSTANCE`, `POLICY`, `CAPABILITIES`, so
splitting the fact from its use would put the operator's policy prose between the
two halves.

## No `requires_tools`

`requires_tools` drops a snippet when a named tool is absent or hidden by
`PAPERLESS_MCP_TOOLS_ALLOW` / `_DENY`. It resolves against tool names only:
`_retained` subtracts `effective_tool_names`, and resources are never consulted.

Half of what this snippet describes *is* resources, which the visibility rule
does not touch. Naming `get_document` would therefore delete the instance URL
and the whole resource map for an operator who merely hid that one tool. The
prose says "the document tools" instead, and the snippet survives any visibility
configuration.

## The URL comes from the staged context

`add_instance_instructions` reads `tool_context_for(mcp).public_url`, not
`make_server`'s `config` argument, and this is the load-bearing choice on the
page.

`register_tools` builds its `ToolContext` from `ProjectConfig.from_env()`; a
config passed to `make_server(config=...)` does not reach the Paperless client
(pvliesdonk/fastmcp-server-template#622). The two therefore *can* name different
instances. Since `web_url` and `share_url` in every tool result are built from
the staged context's `public_url`, reading the passed config here would let the
instructions announce one instance while every link the server emits pointed at
another. That is the one way this snippet could be worse than saying nothing, so
the snippet follows the links rather than the configuration object.

Reading the staged context also removes the empty-URL case: `build_tool_context`
refuses to build a context without a URL, so a staged context always has one and
the function needs no guard. `upstream_version_provider` reads the same staged
context for the same reason.

`tests/unit/test_server_boot.py::test_instance_snippet_names_the_url_tool_results_use`
pins this by handing `make_server` a config whose URL differs from the
environment's and asserting the environment's URL is the one stated.

## A URL with whitespace is refused

The snippet interpolates an operator-supplied URL into model-facing prose, twice.
`env()` strips only *surrounding* whitespace, so a value carrying an embedded
blank line survived into `public_url` and would have rendered as an extra
top-level paragraph in the instructions, indistinguishable from a real
instruction block.

No trust boundary is crossed by that (the same operator already owns
`PAPERLESS_MCP_INSTRUCTIONS_EXTRA`, which is arbitrary model-facing prose by
design), but the failure was silent and its symptom — a model behaving oddly —
pointed nowhere near the configuration. `ProjectConfig.__post_init__` now
rejects whitespace in either URL field, which also protects the `web_url` and
`share_url` links built from the same field and the httpx `base_url` built from
its sibling.

## A migration site inside a seeded file

`domain.py` is listed in the template's `_skip_if_exists`, so `copier update`
never re-renders it. Before this change it imported nothing from
`fastmcp_pvl_core`; it now imports `InstructionRole` and `instructions_for`.
The next pvl-core major that reshapes the instructions API therefore has a call
site here that no template update will fix for us. That is the accepted cost of
contributing a snippet from domain code at all, and it is the first thing to
check when a pvl-core major lands.

## Budget

pvl-core targets 1,536 UTF-16 units of generated guidance, reserving the rest of
Claude Code's 2,048-unit limit for operator routing and policy, and warns rather
than truncates when either is crossed. The composed text with this snippet is
about 590 units, the exact figure depending on the URL's length because it
appears twice.
