# wagtail-cli

> 🚧 This is a prototype / early MVP. Feedback very welcome! See [CMS with AI, not AI CMS: Wagtail 8.0's new API](https://wagtail.org/blog/cms-with-ai-not-ai-cms-wagtail-80s-new-api/) for context.

A command-line client for the Wagtail v3 API. Install it, point it at a site's
API, and your CMS is available from the terminal — for local dev, live sites,
and AI agents. Manage pages, images, documents, snippets, sites, locales, and
redirects, read the Wagtail docs as Markdown, and scaffold new projects.

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

Reading the Wagtail docs needs no configuration at all:

```bash
wt docs releases/8.0    # release notes, as Markdown
wt docs api             # index of v3 API operations
wt docs search picture  # search the docs
```

Create and publish a blog page from a Markdown file:

```bash
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Hello world" --field body:@post.md --publish
```

Rich-text fields accept Markdown via a `.md` file reference: the value is sent
to the API as `{"format": "db_markdown", "content": …}`.

## Command surface

- **`wt api`** — the whole v3 API as commands: `pages`, `images`, `documents`,
  `snippets`, `sites`, `locales`, `redirects`, `schema`, plus `wt api init`
  and `wt api whoami`.
- **`wt docs`** — docs.wagtail.org as Markdown: release notes, the v3 API
  reference, and search.
- **`wt start`** — scaffold a new Django/Wagtail project (mirrors
  `wagtail start` / `django-admin startproject`, with a custom base page model
  as the default).
- **Delegation** — any other `wt <command>` is forwarded to `./manage.py` (if
  present) or `django-admin` (when `DJANGO_SETTINGS_MODULE` is set), so `wt`
  also fronts Django commands like `wt runserver` and `wt makemigrations`.
- **`wt --version` / `wt --help`** — enhanced with detected Wagtail/Django
  versions and `./manage.py --help` when available.

## Documentation

The documentation is published at <https://wagtail.github.io/wagtail-cli/>.

- [Getting started](docs/getting-started.md) — end-to-end walkthrough against the demo site.
- [Command reference](docs/usage.md) — every command and flag.
- [Configuration](docs/reference/configuration.md) — config cascade, dotfiles, environment variables.
- [Agent skills](docs/agent-skills.md) — the machine-readable skill published for AI agents.
- [Development guide](docs/contributing/development.md) — layout, testing, and how to add commands.

## Development

```bash
just install           # set up the environment
just test              # run the test suite
just lint              # lint with Ruff
just test-integration  # run integration tests against a live site
```

See the [development guide](docs/contributing/development.md) for details.
