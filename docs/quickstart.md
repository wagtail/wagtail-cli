# Quickstart

This walkthrough drives the Wagtail v3 API with `wt` from end to end: install,
point it at a site, verify auth, and publish a page with rich-text (Markdown) content.

## 1. Install

```bash
# one-shot (no install)
uvx --from wagtail-cli wt --help

# or install permanently
uv tool install wagtail-cli
wt --help
```

## 2. Configure a site

You need two things: the API base URL and a token. The demo site in this repo
ships with the v3 API mounted at `/api/v3/`; start it and create a token:

```bash
# from the repo root, in the demo/ project
cd demo
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:9001
# in another terminal:
.venv/bin/python manage.py api_tokens create --user=demo
# → prints a token like wagtail_xxxxxxxxxxxxxxxxxxxxxxxx
```

> The v3 API lets authenticated clients create, read, update, and manage
> content. Tokens are tied to user accounts; create one for a superuser or a
> least-privilege role.

Then configure the CLI:

```bash
# env vars (simplest; also sets it for scripts)
export WAGTAIL_CLI_BASE_URL="http://127.0.0.1:9001/api/v3"
export WAGTAIL_CLI_TOKEN="wagtail_xxxxxxxxxxxxxxxxxxxxxxxx"

# or persist it once:
wt api init
# prompts for URL + token and writes ~/.wagtail-cli.toml
```

See [Configuration](configuration.md) for the full precedence rules.

## 3. Verify authentication

```bash
wt api whoami
# {"user": {"username": "demo", ...}, "profile": {...}, "groups": []}
```

## 4. Browse pages and the content model

```bash
wt api pages list --limit 5        # paginated, JSON when piped
wt api schema list                 # registered page types and snippets
wt api schema show blog.BlogPage   # the raw JSON read/create/patch schema
```

`pages list` is a good sanity check: an error here usually means a bad URL,
token, or API path.

## 5. Publish a page written in Markdown

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

- `@post.md` reads the file; because of the `.md` suffix the CLI sends the value
  as `{"format": "db_markdown", "content": "…"}` — the API converts to database
  HTML. A `.html` file (or a plain `--field body:'<p>…</p>'`) is sent as-is.
  `@-` reads from stdin.
- `--parent /blog/` resolves a URL path to a page id via the API's `find`
  endpoint (numeric ids also work, e.g. `--parent 5`).
- `--field` is repeatable and JSON-aware: values starting with `[` or `{` are
  parsed as JSON, so you can set StreamField bodies and structured fields
  directly: `--field 'tags:["bread","sourdough"]'`.
- Without `--publish` the page is created as a draft.

## 6. Verify it's live

```bash
wt api pages list --search "Philosophy of Bread"
wt api pages get <ID> --version live
```

Open the page in a browser if you like:
`http://127.0.0.1:9001/blog/a-philosophy-of-bread/`.

## Mutating commands: `--dry-run` and confirmation

Every mutating command supports `--dry-run`, which prints the request that
*would* be sent without sending it:

```bash
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Dry" --field body:@post.md --dry-run
# POST http://127.0.0.1:9001/api/v3/pages/
# { ...payload... }
```

`update` and `delete` also require confirmation (`--yes`) on a non-interactive
terminal, to keep scripts from destructively mutating content by accident.
