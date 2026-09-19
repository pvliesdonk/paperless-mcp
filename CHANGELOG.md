# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

<!-- version list -->

## 2.1.0-rc.0 (2026-09-19)

### Features

- name the Paperless instance the server fronts (#147)
- give every tool a human-readable title (#148)
- cap inline document content and page through it (#150)

### Bug Fixes

- declare the deferred reindex a bulk edit queues (#151)

## 2.0.0 (2026-09-17)

### Breaking Changes

- the shipped `compose.yml` no longer carries the Traefik
labels
or `build: .` and publishes `8000:8000` against the published image; the
container image ignores `PAPERLESS_MCP_PORT` because its `CMD` pins
`--port 8000`, so a host mapping that relied on it now points at a
closed port;
container and systemd logs change from the Rich layout to one-line JSON
/

### Features

- report the Paperless-NGX version in get_server_info (#121)

### Bug Fixes

- say which version question the remote-version surfaces answer (#127)
- tolerate naive datetimes and int related_document from live Paperless (#134)

## 2.0.0-rc.1 (2026-09-17)

### Breaking Changes

- the shipped `compose.yml` no longer carries the Traefik
labels
or `build: .` and publishes `8000:8000` against the published image; the
container image ignores `PAPERLESS_MCP_PORT` because its `CMD` pins
`--port 8000`, so a host mapping that relied on it now points at a
closed port;
container and systemd logs change from the Rich layout to one-line JSON
/

### Features

- report the Paperless-NGX version in get_server_info (#121)

### Bug Fixes

- say which version question the remote-version surfaces answer (#127)
- tolerate naive datetimes and int related_document from live Paperless (#134)

## 2.0.0-rc.0 (2026-09-16)

### Breaking Changes

- the shipped `compose.yml` no longer carries the Traefik
labels
or `build: .` and publishes `8000:8000` against the published image; the
container image ignores `PAPERLESS_MCP_PORT` because its `CMD` pins
`--port 8000`, so a host mapping that relied on it now points at a
closed port;
container and systemd logs change from the Rich layout to one-line JSON
/

### Features

- report the Paperless-NGX version in get_server_info (#121)

### Bug Fixes

- say which version question the remote-version surfaces answer (#127)

## 1.0.2 (2026-08-25)

### Bug Fixes

- rebuild create_download_link on pvl-core's Transfer API (#75)

## 1.0.2-rc.0 (2026-08-25)

### Bug Fixes

- rebuild create_download_link on pvl-core's Transfer API (#75)

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
