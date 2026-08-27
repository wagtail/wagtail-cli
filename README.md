# wagtail-cli

> 🚧 This is a prototype / early MVP. Feedback very welcome! See [CMS with AI, not AI CMS: Wagtail 8.0’s new API](https://wagtail.org/blog/cms-with-ai-not-ai-cms-wagtail-80s-new-api/) for context.

A command-line client for the Wagtail v3 API. Install it, point it at a Wagtail
site's API, and drive CMS operations (pages, images, documents, snippets, sites,
locales, redirects, schema) from your terminal — handy for automation and
AI-orchestrated content management.

## Installation

Pick the command for your preferred package installer. The console script is
`wt` (the package name is `wagtail-cli`):

```bash
uv tool install wagtail-cli      # permanent install; then run `wt …`
uvx --from wagtail-cli wt       # one-shot, no install
```

## Quick start

```bash
export WAGTAIL_CLI_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_CLI_TOKEN="your-api-token"

wt api whoami        # verify authentication
wt api pages list    # browse pages
wt api schema list   # discover page types
```

Or run `wt api init` once to save these to `~/.wagtail-cli.toml` interactively.

Create and publish a blog page from a Markdown file:

```bash
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Hello world" --field body:@post.md --publish
```

Rich-text fields accept Markdown via a `.md` file reference: the value is sent
to the API as `{"format": "db_markdown", "content": …}`.

## Command surface

- **`wt api …`** — all Wagtail v3 API operations (`pages`, `images`,
  `documents`, `snippets`, `sites`, `locales`, `redirects`, `schema`), plus
  `wt api init` and `wt api whoami`.
- **`wt start …`** — scaffold a new Django/Wagtail project (mirrors
  `wagtail start` / `django-admin startproject`; default custom base-page template).
- **Delegation** — any other `wt <command>` is forwarded to `./manage.py` (if
  present) or `django-admin` (when `DJANGO_SETTINGS_MODULE` is set), so `wt`
  also fronts Django commands like `wt runserver`/`wt makemigrations`.
- **`wt --version` / `wt --help`** — custom, enhanced with detected Wagtail/Django
  versions and `./manage.py --help` when available.

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
