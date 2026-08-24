# Command reference

`wt` is organized as a Typer app with a `pages`/`images`/`documents`/
`snippets`/`sites`/`locales`/`redirects`/`schema` command groups and two
top-level commands, `whoami` and `init`.

## Global options

Available on every invocation (before or after the command name):

| Flag | Description |
|---|---|
| `--url URL` | API base URL (overrides config/env). |
| `--token TOKEN` | API token (overrides config/env). |
| `--json` | Force JSON output. |
| `--human` | Force human-readable output. |
| `-v` / `--verbose` | Print HTTP request/response details to stderr. |
| `--dry-run` | Print the request that would be sent, without sending it. |
| `--version` | Print version and exit. |

`--json` and `--human` are mutually exclusive (the CLI exits with a usage
error if both are given).

## Output conventions

- **JSON when piped**, human-readable when on a terminal.
- `--json` / `--human` override auto-detection. Human lists render as a table
  (id/title/name/label columns by default); details render as key/value lines.
- `--dry-run` prints `METHOD url`, `Params`, and the JSON body that would be
  sent, and makes no network call.
- `schema show` always outputs JSON (the schema is the machine-readable contract).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General / unexpected error |
| 2 | Usage / argument error (incl. `--json --human`, missing `--yes`) |
| 3 | Network / connection error |
| 4 | Authentication error (401) |
| 5 | Permission denied (403) |
| 6 | Not found (404) |
| 7 | Validation error (400/422) |

Errors print `Error (status): message` plus the RFC 7807 body verbatim to
stderr.

---

## `wt whoami`

Print the authenticated user, profile, and groups.

## `wt init`

Interactive setup: prompts for URL + token (unless both flags are given),
tests the connection, and writes `~/.wagtail-cli.toml`.

## `wt schema`

Discover the content model.

```
wt schema list
wt schema show <TYPE>       # e.g. blog.BlogPage — raw JSON schema
```

## `wt pages`

Read, create, and manage pages, including actions and revisions.

```
wt pages list [--type T]* [--child-of REF] [--descendant-of REF]
                [--ancestor-of REF] [--translation-of N] [--locale CODE] [--site N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt pages find [--id N] [--path /blog/] [--site N]
wt pages get <ID> [--version draft|live] [--html]
wt pages create <TYPE> --parent REF --title T
                [--slug S] [--field K:V]... [--publish]
wt pages update <ID> [--title T] [--slug S] [--field K:V]... [--publish] [--yes]
wt pages delete <ID> [--yes]
wt pages publish <ID>
wt pages unpublish <ID>
wt pages copy <ID> --destination REF [--slug S] [--title T]
                [--recursive/--no-recursive] [--keep-live/--no-keep-live]
wt pages move <ID> --destination REF
wt pages revert <ID> --revision N
wt pages create-alias <ID> --destination REF
wt pages convert-alias <ID>
wt pages copy-for-translation <ID> --locale CODE
wt pages revisions list <ID> [--limit N] [--offset N]
wt pages revisions get <ID> <REVISION_ID>
```

`REF` is a page id or a URL path (e.g. `/blog/`), resolved through the API's
find endpoint. `--field` values that start with `[` or `{` are parsed as JSON;
`@file` reads a value from a file (`@-` = stdin). Multi-line rich-text bodies
read from a `.md` file are sent with `format: db_markdown`.

## `wt images`

Upload and manage images.

```
wt images list [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt images get <ID>
wt images create <FILE> --title T [--field K:V]...     # multipart upload
wt images update <ID> [--title T] [--field K:V]... [--yes]
wt images delete <ID> [--yes]
```

## `wt documents`

Upload and manage documents.

```
wt documents list [--search Q] [--search-operator and|or] [--order F]
                   [--limit N] [--offset N]
wt documents get <ID>
wt documents create <FILE> --title T [--field K:V]...  # multipart upload
wt documents update <ID> [--title T] [--field K:V]... [--yes]
wt documents delete <ID> [--yes]
```

## `wt snippets`

Manage API-enabled snippets. The snippet type is always required (each snippet
model lives in its own table).

```
wt snippets list <TYPE> [--locale CODE] [--translation-of N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt snippets get <TYPE> <PK>
wt snippets create <TYPE> [--field K:V]...
wt snippets update <TYPE> <PK> [--field K:V]... [--yes]
wt snippets delete <TYPE> <PK> [--yes]
wt snippets publish <TYPE> <PK>
wt snippets unpublish <TYPE> <PK>
wt snippets revert <TYPE> <PK> --revision N
wt snippets copy-for-translation <TYPE> <PK> --locale CODE
wt snippets revisions list <TYPE> <PK> [--limit N] [--offset N]
wt snippets revisions get <TYPE> <PK> <REVISION_ID>
```

## `wt sites`

Manage sites.

```
wt sites list [--limit N] [--offset N]
wt sites get <ID>
wt sites create --field K:V...      # e.g. hostname, root_page_id (required)
wt sites update <ID> --field K:V... [--yes]     # PUT: all required fields
wt sites delete <ID> [--yes]
```

## `wt locales`

Manage locales.

```
wt locales list [--limit N] [--offset N]
wt locales get <ID>
wt locales create --field K:V...    # e.g. language_code (required)
wt locales update <ID> --field K:V... [--yes]    # PUT: language_code required
wt locales delete <ID> [--yes]
```

## `wt redirects`

Manage redirects.

```
wt redirects list [--order F] [--limit N] [--offset N]
wt redirects find [--id N] [--path /old/]
wt redirects get <ID>
wt redirects create --field K:V...  # e.g. old_path (required)
wt redirects update <ID> --field K:V... [--yes]   # PUT: old_path required
wt redirects delete <ID> [--yes]
```

---

## Confirmations

Commands that mutate-or-destroy an existing object (`update`, `delete`) gate on
`--yes` on a TTY (they prompt for confirmation otherwise; piped/scripted
invocations never prompt, so pass `--yes` there).

Commands that perform an action (`publish`, `unpublish`, `revert`,
`copy-for-translation`) execute immediately without a confirmation prompt —
preview them with `--dry-run` instead.

```
wt --dry-run pages publish 42
wt pages delete 42 --yes
```

---

## `--field` value parsing

`--field KEY:VALUE` is repeatable. Value handling:

- `[` or `{` prefix → parsed as JSON (arrays, objects, nested structures).
- `@path` → read the value from a file; `@-` from stdin.
  - `.md` file → wrapped as `{"format": "db_markdown", "content": "…"}`.
  - `.json` file → parsed as JSON.
  - other → sent as the raw file text.
- otherwise → sent as the raw string.

Example: `--field 'body:[{"type":"paragraph","value":"<p>Hi</p>","id":"abc"}]'`.