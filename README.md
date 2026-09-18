# [Wagtail CLI](https://wagtail.github.io/wagtail-cli)

> 🚧 This is a prototype. Feedback very welcome! See [CMS with AI, not AI CMS: Wagtail 8.0's new API](https://wagtail.org/blog/cms-with-ai-not-ai-cms-wagtail-80s-new-api/) and [Prototyping a new CLI for Wagtail](https://wagtail.org/blog/prototyping-a-cli-for-wagtail/) for context.

Speed up and automate Wagtail operations with the command line. Key features:

- v3 write API client. 50+ CMS admin operations available from the terminal. To help manage local development and live sites. Manage pages, images, documents, snippets, sites, locales, redirects, and more.
- Read and search Wagtail docs as Markdown.
- Scaffold new Django/Wagtail projects.

## Installation

Install [`wagtail-cli`](https://pypi.org/project/wagtail-cli/) from PyPI with your preferred package manager, then use the `wt` CLI. Example with `uv`:

```bash
# Permanent install:
uv tool install wagtail-cli
# One-off usage:
uvx --from wagtail-cli wt
```

## Quick start

```bash
export WAGTAIL_CLI_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_CLI_TOKEN="your-api-token"

wt api whoami        # verify authentication
wt api pages list    # browse pages
wt api schema list   # discover page types
```

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

- [Getting started](https://wagtail.github.io/wagtail-cli/getting-started/) — end-to-end walkthrough against the demo site.
- [Command reference](https://wagtail.github.io/wagtail-cli/usage/) — every command and flag.
- [Configuration](https://wagtail.github.io/wagtail-cli/reference/configuration/) — config cascade, dotfiles, environment variables.
- [Agent skills](https://wagtail.github.io/wagtail-cli/agent-skills/) — the machine-readable skill published for AI agents.

## Contributing

See the [development guide](docs/contributing/development.md) for details.
