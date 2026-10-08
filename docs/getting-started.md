# Getting started

The CLI requires a recent Python version. Its (optional) API client requires a exposing the [v3 API](https://docs.wagtail.org/en/stable/advanced_topics/api/v3/index.html).

## Installation

Install [`wagtail-cli`](https://pypi.org/project/wagtail-cli/) from PyPI with your preferred package manager, then use the `wt` CLI. Example with `uv`:

```bash
# Permanent install:
uv tool install wagtail-cli
# One-off usage:
uvx --from wagtail-cli wt
# Done!
wt --help
```

Note: some of the CLI’s functionality relies on detecting your project’s environment. We do our best to identify it, but it’s always better to run it directly within your virtual environment.

### Install the skill

Optionally, install the one skill that helps agents with everything Wagtail. There are multiple options depending on your needs. To install directly as a skill, for multiple agents / harnesses:

```bash
# Directly with the CLI, global:
mkdir -p ~/.agents/skills/wagtail && wt skills get wagtail > ~/.agents/skills/wagtail/SKILL.md
# Directly with the CLI, local:
mkdir -p .agents/skills/wagtail && wt skills get wagtail > .agents/skills/wagtail/SKILL.md
```

#### As a plugin

It’s also available as a plugin, follow [Agent Plugins compatible clients](https://agent-plugins.org/compatible-clients) installation instructions, using this repository as the plugin source: `wagtail/wagtail-cli`.

## Quick start

### Docs access

Reading the Wagtail docs needs no configuration at all:

```bash
wt docs releases/8.0    # release notes, as Markdown
wt docs api             # index of v3 API operations
wt docs search picture  # search the docs
```

### API usage

You will need to configure the needed API credentials before using the API commands:

```bash
# Create your API token:
wt api_tokens create --user=demo
# This is the same as:
./manage.py api_tokens create --user=demo

export WAGTAIL_CLI_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_CLI_TOKEN="your-api-token"

wt api whoami        # verify authentication
wt api pages list    # browse pages
wt api schema list   # discover page types
```

If you want, you can persist the API credentials with `wt api init`. Keep the generated file private.

See [Configuration](reference/configuration.md) for the full precedence rules on managing credentials.

## API operations

### Browse pages and the content model

```bash
wt api pages list --limit 5        # paginated, JSON when piped
wt api schema list                 # registered page types and snippets
wt api schema show blog.BlogPage   # the raw JSON read/create/patch schema
```

`pages list` is a good sanity check: an error here usually means a bad URL, token, or API path.

### Publish a page written in Markdown

Create a local Markdown file:

```bash
cat > post.md <<'EOF'
## A Philosophy of Bread

Wagtail's v3 API accepts Markdown for rich-text fields and converts it server-side.
EOF
```

Create and publish a page whose `body` field is rich text:

```bash
wt api pages create blog.BlogPage \
  --parent /blog/ \
  --title "A Philosophy of Bread" \
  --field body:@post.md \
  --publish
```

What happens:

- `@post.md` reads the file; because of the `.md` suffix the CLI sends the value as `{"format": "db_markdown", "content": "…"}` — the API converts to database HTML. A `.html` file (or a plain `--field body:'<p>…</p>'`) is sent as-is. `@-` reads from stdin.
- `--parent /blog/` resolves a URL path to a page id via the API's `find` endpoint (numeric ids also work, e.g. `--parent 5`).
- `--field` is repeatable and JSON-aware: values starting with `[` or `{` are parsed as JSON, so you can set StreamField bodies and structured fields directly: `--field 'tags:["bread","sourdough"]'`.
- Without `--publish` the page is created as a draft.

### Verify it's live

```bash
wt api pages list --search "Philosophy of Bread"
wt api pages get <ID> --version live
```

Open the page in a browser if you like: `http://127.0.0.1:9001/blog/a-philosophy-of-bread/`.

### Mutating commands: `--dry-run` and confirmation

Every mutating command supports `--dry-run`, which prints the request that _would_ be sent without sending it:

```bash
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Dry" --field body:@post.md --dry-run
# POST http://127.0.0.1:9001/api/v3/pages/
# { ...payload... }
```

`update` and `delete` also require confirmation (`--yes`) on a non-interactive terminal, to keep scripts from destructively mutating content by accident.

### Next steps

- [Usage](usage.md) – the full command reference, every command and flag.
- [Configuration](reference/configuration.md) – the config cascade, dotfiles, and environment variables.
- [Agent skills](agent-skills.md) – point an AI agent at the published skill.
