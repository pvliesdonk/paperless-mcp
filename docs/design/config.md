# Configuration design

Internal design note. Not published; not Vale-linted.

## Where the Paperless variables live

The six `PAPERLESS_MCP_*` domain variables — `PAPERLESS_URL`, `API_TOKEN`,
`HTTP_TIMEOUT_SECONDS`, `HTTP_RETRIES`, `DEFAULT_PAGE_SIZE`,
`PAPERLESS_PUBLIC_URL` — are flat fields on `ProjectConfig`, declared between
the `CONFIG-FIELDS` sentinels in `src/paperless_mcp/config.py`, read between the
`CONFIG-FROM-ENV` sentinels, and validated between the `CONFIG-VALIDATE` ones.
`scripts/gen_config_surface.py` discovers them by AST-scanning `from_env` and
pairing each literal `env(prefix, "SUFFIX")` read with the matching field's
`metadata={"help", "tags", "wizard"}`. Every generated artifact — the two env
examples, `examples/*.env`, the wizard spec, the two documentation tables,
`server.json`, the mcpb manifest and the Claude plugin pair — comes from those
declarations.

They used to live in a `pydantic-settings` `BaseSettings` class
(`_domain_config.py`) and be hand-declared under `vars:` in
`config-presentation.domain.yml`. That route is documented for variables the
scan *cannot* see; nothing prevented it from seeing these, so the declaration
and the code that read it were two sources for one fact, and the project
carried `pydantic-settings` for those six fields alone.

`make_server` resolves `ProjectConfig` once and binds that object to the server
before any registrar runs. `tool_context_for` reads the bound object, so a
caller-supplied config reaches the Paperless client and schema-time defaults
without a second environment read.

## How the template contract shapes it

### `env_int` / `env_float` are not importable

`config.py` is re-rendered by `copier update` and only its three sentinel blocks
survive. The template's import block brings in `ServerConfig`,
`TransferConfig`, `env` and `ConfigurationError` and nothing else, so adding `env_int` / `env_float` — or importing a parsing helper
from another module — would be an edit outside every seam. The numeric reads are
therefore parsed inline (`float(env(...) or 30.0)`) and their bounds are
enforced in `__post_init__`, which is where the config contract wants invariants
anyway: `env_float`'s bounds check only the env-sourced value, so a direct
`ProjectConfig(http_timeout_seconds=0)` would slip past them.

The cost: a malformed value now raises `float()`'s or `int()`'s own message,
which does not name the variable, where `env_float(strict=True)` would have.

### Required variables

`PAPERLESS_URL` and `API_TOKEN` are read with `env(..., required=True)` in
`from_env` (template v10.3, fastmcp-pvl-core 10.1). An unset one raises
`ConfigurationError`, which `serve` prints as one line, and the generated
tables mark both required. The fields keep `default=""` only for dataclass
field ordering, so a direct `ProjectConfig()` still constructs; tests get the
pair from `config_contract_env` in `tests/conftest.py`.

`domain.build_tool_context` keeps its own check, now a `ConfigurationError`,
for the one path `from_env` does not cover: a config built by hand and passed
to `make_server`. `CONFIG-VALIDATE` raises `ConfigurationError` too, for the
same one-line exit.

### Registration reads the bound config

`make_server` calls `bind_config(mcp, config)` before `register_tools(mcp)` and
the other registrars. `tool_context_for` retrieves that exact object through
`config_for(mcp)`, so `default_page_size`, the Paperless client, and the
instance URL all reflect a config passed directly to `make_server`. A test that
uses a bare `FastMCP` with the top-level registrars must bind a config first;
there is deliberately no environment fallback that could recreate the old
divergence.

`build_tool_context(config)` itself still reads no environment, so the context
remains constructible from a plain `ProjectConfig(...)`. This closes
pvliesdonk/fastmcp-server-template#622.

## Field semantics worth keeping

Two details the deleted `DomainConfig` docstring carried and the generated help
text has no room for: `HTTP_TIMEOUT_SECONDS` applies to connect, read, write and
pool independently (it is handed to `httpx.Timeout` as a single value), and
`HTTP_RETRIES` counts retries *after* the initial attempt, so `2` means up to
three requests.

## Secrets

`api_token` was a `pydantic.SecretStr`, whose `repr` printed `**********`. As a
plain `str` on a dataclass it would print in every `repr(config)`, so the field
carries `repr=False`. Outbound `Authorization` headers are separately masked in
logs by `_SecretMaskFilter` in `client/_http.py`.

## Transfer configuration

`ProjectConfig.transfer` composes core's `TransferConfig` and calls its
`from_env` reader. The generated config reference and environment examples
include its five variables. The subsystem is activated for HTTP/SSE only when
`ServerConfig.base_url` is set; see [document transfers](document-transfers.md)
for the compatibility choice and URL routing contract.
