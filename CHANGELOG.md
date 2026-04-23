# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 0.1.0 - 2026-04-23

### Added
- Initial release.
- Full parity with the existing community `paperless-mcp` tool surface.
- Read-only observability additions: `list_tasks`, `wait_for_task`,
  `get_statistics`, `get_remote_version`, `get_document_metadata`,
  `get_document_history`, `get_document_suggestions`, `list_storage_paths`,
  `list_saved_views`, `list_share_links`, plus their `get_*` variants.
- MCP resources for all entity types plus per-document templated URIs.
- `create_download_link` tool backed by `fastmcp_pvl_core.ArtifactStore`.
- Lucide icons on every tool.
- Read-only mode toggle via `PAPERLESS_MCP_READ_ONLY`.
