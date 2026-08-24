# Task 3 Report: pvl-core 4.3 Server Wiring

## Scope Completed

- Removed the unsupported `create_download_link` registration path and deleted
  `src/paperless_mcp/tools/downloads.py`.
- Removed `ToolContext.artifact_store`, the internal `DownloadLink` response
  model, and `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` configuration.
- Preserved the v2.11 server lifespan: one managed `PaperlessClient` is passed
  through `ToolContext`, is used to register tools/resources/prompts, and is
  closed during shutdown.
- Preserved HTTP construction with the KV-backed event store selected by
  `PAPERLESS_MCP_KV_STORE_URL=memory://`.
- Updated active operator documentation and configuration examples to remove
  the unavailable download-link tool and its TTL setting.
- Did not modify `docs/javascripts/config-wizard/wizard-spec.json`; Task 4
  owns config-wizard drift remediation.

## Changed Public Behavior

- `create_download_link` is no longer listed or callable on any transport.
- `PAPERLESS_MCP_DOWNLOAD_LINK_TTL_SECONDS` is no longer a supported setting.
- Download links remain intentionally unavailable until the supported
  TransferSink replacement is introduced in the v5.3 stage.

## Tests and Checks

- `uv lock`
- `uv sync --all-extras --all-groups --locked`
- `uv run pytest tests/unit/test_server_boot.py tests/unit/tools/test_downloads.py -q`
  - 3 passed before the production removal and 3 passed afterward. The new
    registry assertion passes before removal because the old implementation
    conditionally skipped registration when no artifact store was supplied;
    it remains the required final regression guard.
- `uv run ruff check --fix .`
  - Passed.
- `uv run ruff format .`
  - Applied formatting once; subsequent check reported 114 files already
    formatted.
- `uv run ruff format --check .`
  - Passed.
- `uv run pytest -x -q --ignore=tests/test_config_wizard_drift.py`
  - 242 passed, 17 skipped (integration/site-build prerequisites).
- `uv run mypy src/ tests/`
  - Passed with no issues in 111 source files.
- `uv run diff-quality --violations=ruff.check --options="--extend-select=C901,PLR0911,PLR0912,PLR0913,PLR0915,S" --compare-branch=origin/main --fail-under=100`
  - Blocked at 99% by pre-existing branch changes in
    `scripts/copier_update_aggregator.py`, not by Task 3 files.

## Active EVENT_STORE_URL Search

`git grep -n 'EVENT_STORE_URL'` returns one result:

```text
docs/javascripts/config-wizard/wizard-spec.json:165:      "var": "PAPERLESS_MCP_EVENT_STORE_URL",
```

This is the config-wizard compatibility/drift entry reserved for Task 4. There
are no active runtime, Compose, server-registry, or operator-documentation
references outside that Task 4-owned file.

## Concerns

- The complete suite currently fails at
  `tests/test_config_wizard_drift.py::test_wizard_covers_full_env_surface` for
  `OIDC_ADVERTISED_SCOPES`, `TASKS_URL`, `TOOLS_ALLOW`, and `TOOLS_DENY`.
  This is the known Task 4 scope and was intentionally not remediated here.
- The structural diff gate is blocked by two existing functions in
  `scripts/copier_update_aggregator.py`: `_render_job_b` and `_render_job_c`
  exceed C901/PLR0911/PLR0912 limits in the branch-wide comparison.
- The specified registry regression cannot reproduce a red phase in this
  checkout because the removed tool was already skipped when the test context
  had no artifact store. The test still verifies the required final public
  registry behavior.

## Fix Round 1

- Added `test_sse_server_boots_without_artifact_store` in
  `tests/unit/test_server_boot.py`. It exercises the non-stdio transport path
  that the retired server wired to `ArtifactStore`, without recreating or
  faking that removed API. The current server constructs successfully; the
  retired wiring would fail against pvl-core 4 because `ArtifactStore` is no
  longer available.
- Kept `test_tool_registry_omits_download_link` unchanged as the final public
  registry assertion.
- Ran `uv run pytest tests/unit/test_server_boot.py tests/unit/tools/test_downloads.py -q`.
  Output: `4 passed in 0.41s`.
