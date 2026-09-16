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
and the code that read it were two sources for one fact, and the server parsed
the environment twice per start.

## Three constraints that shaped the result

### `env_int` / `env_float` are not importable

`config.py` is re-rendered by `copier update` and only its three sentinel blocks
survive. The template's import block brings in `ServerConfig` and `env` and
nothing else, so adding `env_int` / `env_float` — or importing a parsing helper
from another module — would be an edit outside every seam. The numeric reads are
therefore parsed inline (`float(env(...) or 30.0)`) and their bounds are
enforced in `__post_init__`, which is where the config contract wants invariants
anyway: `env_float`'s bounds check only the env-sourced value, so a direct
`ProjectConfig(http_timeout_seconds=0)` would slip past them.

The cost: a malformed value now raises `float()`'s or `int()`'s own message,
which does not name the variable, where `env_float(strict=True)` would have.

### A required field cannot be expressed

`_is_required` in the generator marks a domain variable required when its field
declares neither a `default` nor a `default_factory`. A dataclass field with no
default cannot follow fields that have one unless it is `kw_only`, and either
way `ProjectConfig()` stops being constructible — which the template's own
`tests/test_config_contract.py` does four times. So the two genuinely required
variables carry `default=""`, and the requirement is enforced in
`domain.build_tool_context`, which raises `ValueError` naming whichever is
unset. The failure point is unchanged from v1.0.2: registration is the first
thing `make_server` does that needs a client.

The visible cost: the `Required` column in `README.md` and `docs/configuration.md`
reads `No` for both, so their descriptions and the hand-written prose above the
table carry the requirement instead. Filed upstream as
pvliesdonk/fastmcp-server-template#621.

### The config does not reach registration

`make_server` resolves a `ProjectConfig` and then calls `register_tools(mcp)`
without it; `server.py` is template-owned, and the one block this project may
add code to — `DOMAIN-WIRING` — runs *after* registration. `default_page_size`
is a tool parameter default baked into the tool schema *during* registration, so
a later rebind could not fix what registration already wrote. `tool_context_for`
therefore falls back to `ProjectConfig.from_env()` when nobody hands it a
config, exactly as `load_domain_config()` did before.

`build_tool_context(config)` itself reads no environment, so the context is
constructible in a test from a plain `ProjectConfig(...)`, and `register_tools`
/ `register_resources` accept a pre-built context. Filed upstream as
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
