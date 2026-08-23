# wgtl-api-cli

A command-line client for the Wagtail v3 API. Install it, point it at a Wagtail
site's API, and drive CMS operations (pages, images, documents, snippets, sites,
locales, redirects, schema) from your terminal — handy for automation and
AI-orchestrated content management.

## Installation

Pick the command for your preferred package installer. The console script is
`wgtl` (the package name is `wgtl-api-cli`):

```bash
uv tool install wgtl-api-cli      # permanent install; then run `wgtl …`
uvx --from wgtl-api-cli wgtl       # one-shot, no install
```

## Quick start

```bash
export WAGTAIL_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_TOKEN="your-api-token"

wgtl whoami        # verify authentication
wgtl pages list    # browse pages
wgtl schema list   # discover page types
```

Or run `wgtl init` once to save these to `~/.wgtl.toml` interactively.

Create and publish a blog page from a Markdown file:

```bash
wgtl pages create blog.BlogPage --parent /blog/ \
  --title "Hello world" --field body:@post.md --publish
```

Rich-text fields accept Markdown via a `.md` file reference: the value is sent
to the API as `{"format": "db_markdown", "content": …}`.

## Documentation

- [Quickstart](docs/quickstart.md) — end-to-end walkthrough against the demo site.
- [Configuration](docs/configuration.md) — config cascade, dotfiles, environment variables.
- [Command reference](docs/commands.md) — every command and flag.
- [Development](docs/development.md) — layout, testing, and how to add commands.

## Development

```bash
just install           # set up the environment
just test              # run the test suite
just lint              # lint with Ruff
just test-integration  # run integration tests against a live site
```

See the [development guide](docs/development.md) for details.