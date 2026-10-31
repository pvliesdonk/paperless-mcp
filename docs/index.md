---
description: "What Paperless MCP is, what it does, and where to start reading."
kind: explanation
---

# Paperless MCP

Paperless-NGX over MCP: search, read, upload and tag documents; manage correspondents and types.

What the server can reach, what it changes and who gets in is set out in the [security model](security-model.md).

## Where to go

- [Get started](get-started/index.md): a first success with the client you use.
- [Deploy](deploy/index.md): run it for real, in a container and behind authentication.
- [Use](use/index.md): get more out of its features.
- [Reference](reference/configuration.md): configuration, [tools](reference/tools/index.md), resources, prompts and the command line.
- [Upgrade](upgrade/index.md): release channels and what changes when you move.
- [Contribute](contribute/index.md): change the project.

<!-- DOMAIN-INDEX-FEATURES-START -->
## Features

Paperless MCP gives an MCP client the API of an existing Paperless-NGX instance, one tool per operation, with that instance's permissions:

- **Documents:** full-text and filtered search, metadata, notes, history, thumbnails, and the OCR text in bounded sections.
- **Organising:** tags, correspondents, document types and custom fields, one at a time or in bulk.
- **Files:** uploads, and over HTTP one-time [transfer links](deploy/transfer-links.md) for whole files.
- **The instance:** statistics, saved views, storage paths, share links and background tasks.

Every tool is listed in the [tools reference](reference/tools/index.md).
<!-- DOMAIN-INDEX-FEATURES-END -->

<!-- DOMAIN-INDEX-USE-CASES-START -->
## What you can do

With the server connected, a client can handle requests such as:

- "Find last quarter's invoices from ACME."
- "Tag these three documents as 'reviewed' and move them to the Accounting correspondent."
- "Upload this PDF and wait until OCR finishes."
- "What changed on document 4213 in the last week?"

The model picks the tools; the server adds no workflow of its own.
<!-- DOMAIN-INDEX-USE-CASES-END -->
