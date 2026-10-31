# Paperless MCP

Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.

What the server can reach, what it changes and who gets in is set out in the [security model](https://pvliesdonk.github.io/paperless-mcp/unstable/security-model/index.md).

## Where to go

- [Get started](https://pvliesdonk.github.io/paperless-mcp/unstable/get-started/index.md): a first success with the client you use.
- [Deploy](https://pvliesdonk.github.io/paperless-mcp/unstable/deploy/index.md): run it for real, in a container and behind authentication.
- [Use](https://pvliesdonk.github.io/paperless-mcp/unstable/use/index.md): get more out of its features.
- [Reference](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/configuration/index.md): configuration, [tools](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/tools/index.md), resources, prompts and the command line.
- [Upgrade](https://pvliesdonk.github.io/paperless-mcp/unstable/upgrade/index.md): release channels and what changes when you move.
- [Contribute](https://pvliesdonk.github.io/paperless-mcp/unstable/contribute/index.md): change the project.

## Features

Paperless MCP gives an MCP client the API of an existing Paperless-NGX instance, one tool per operation, with that instance's permissions:

- **Documents:** full-text and filtered search, metadata, notes, history, thumbnails, and the OCR text in bounded sections.
- **Organising:** tags, correspondents, document types and custom fields, one at a time or in bulk.
- **Files:** uploads, and over HTTP one-time [transfer links](https://pvliesdonk.github.io/paperless-mcp/unstable/deploy/transfer-links/index.md) for whole files.
- **The instance:** statistics, saved views, storage paths, share links and background tasks.

Every tool is listed in the [tools reference](https://pvliesdonk.github.io/paperless-mcp/unstable/reference/tools/index.md).

## What you can do

With the server connected, a client can handle requests such as:

- "Find last quarter's invoices from ACME."
- "Tag these three documents as 'reviewed' and move them to the Accounting correspondent."
- "Upload this PDF and wait until OCR finishes."
- "What changed on document 4213 in the last week?"

The model picks the tools; the server adds no workflow of its own.
