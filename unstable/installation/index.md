# Installation

## From PyPI

```
pip install pvliesdonk-paperless-mcp
```

## From Docker

```
docker pull ghcr.io/pvliesdonk/paperless-mcp:latest
```

The `latest` tag is the newest stable release. The rolling `edge` tag tracks every merge to `main` and carries no version identity; see [Image tags](https://pvliesdonk.github.io/paperless-mcp/unstable/deployment/docker/#image-tags) for the full list.

## From source

```
git clone https://github.com/pvliesdonk/paperless-mcp
cd paperless-mcp
uv sync --all-extras --all-groups
```
