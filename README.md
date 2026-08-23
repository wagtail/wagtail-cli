# wgtl-api-cli

A command-line client for the Wagtail v3 API. Install it, point it at a Wagtail
site's API, and drive CMS operations (pages, images, documents, snippets, sites,
locales, redirects, schema) from your terminal — handy for automation and
AI-orchestrated content management.

## Installation

Pick the command for your preferred package installer:

```bash
uv tool install wgtl-api-cli
uvx wgtl-api-cli
```

## Quick start

```bash
export WAGTAIL_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_TOKEN="your-api-token"

wgtl whoami
wgtl pages list
```

## Documentation

See the [`docs/`](docs/) folder for the full command reference, configuration
guide, and development notes.

## Development

```bash
just install   # set up the environment
just test      # run the test suite
just lint      # lint with Ruff
```