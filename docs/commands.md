# Command reference

`wgtl` is organized as a Typer app with a `pages`/`images`/`documents`/
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

## `wgtl whoami`

Print the authenticated user, profile, and groups.

## `wgtl init`

Interactive setup: prompts for URL + token (unless both flags are given),
tests the connection, and writes `~/.wgtl.toml`.

## `wgtl schema`

Discover the content model.

```
wgtl schema list
wgtl schema show <TYPE>       # e.g. blog.BlogPage — raw JSON schema
```

## `wgtl pages`

Read, create, and manage pages, including actions and revisions.

```
wgtl pages list [--type T]* [--child-of REF] [--descendant-of REF]
                [--ancestor-of REF] [--translation-of N] [--locale CODE] [--site N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wgtl pages find [--id N] [--path /blog/] [--site N]
wgtl pages get <ID> [--version draft|live] [--html]
wgtl pages create <TYPE> --parent REF --title T
                [--slug S] [--field K:V]... [--publish]
wgtl pages update <ID> [--title T] [--slug S] [--field K:V]... [--publish] [--yes]
wgtl pages delete <ID> [--yes]
wgtl pages publish <ID>
wgtl pages unpublish <ID>
wgtl pages copy <ID> --destination REF [--slug S] [--title T]
                [--recursive/--no-recursive] [--keep-live/--no-keep-live]
wgtl pages move <ID> --destination REF
wgtl pages revert <ID> --revision N
wgtl pages create-alias <ID> --destination REF
wgtl pages convert-alias <ID>
wgtl pages copy-for-translation <ID> --locale CODE
wgtl pages revisions list <ID> [--limit N] [--offset N]
wgtl pages revisions get <ID> <REVISION_ID>
```

`REF` is a page id or a URL path (e.g. `/blog/`), resolved through the API's
find endpoint. `--field` values that start with `[` or `{` are parsed as JSON;
`@file` reads a value from a file (`@-` = stdin). Multi-line rich-text bodies
read from a `.md` file are sent with `format: db_markdown`.

## `wgtl images`

Upload and manage images.

```
wgtl images list [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wgtl images get <ID>
wgtl images create <FILE> --title T [--field K:V]...     # multipart upload
wgtl images update <ID> [--title T] [--field K:V]... [--yes]
wgtl images delete <ID> [--yes]
```

## `wgtl documents`

Upload and manage documents.

```
wgtl documents list [--search Q] [--search-operator and|or] [--order F]
                   [--limit N] [--offset N]
wgtl documents get <ID>
wgtl documents create <FILE> --title T [--field K:V]...  # multipart upload
wgtl documents update <ID> [--title T] [--field K:V]... [--yes]
wgtl documents delete <ID> [--yes]
```

## `wgtl snippets`

Manage API-enabled snippets. The snippet type is always required (each snippet
model lives in its own table).

```
wgtl snippets list <TYPE> [--locale CODE] [--translation-of N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wgtl snippets get <TYPE> <PK>
wgtl snippets create <TYPE> [--field K:V]...
wgtl snippets update <TYPE> <PK> [--field K:V]... [--yes]
wgtl snippets delete <TYPE> <PK> [--yes]
wgtl snippets publish <TYPE> <PK>
wgtl snippets unpublish <TYPE> <PK>
wgtl snippets revert <TYPE> <PK> --revision N
wgtl snippets copy-for-translation <TYPE> <PK> --locale CODE
wgtl snippets revisions list <TYPE> <PK> [--limit N] [--offset N]
wgtl snippets revisions get <TYPE> <PK> <REVISION_ID>
```

## `wgtl sites`

Manage sites.

```
wgtl sites list [--limit N] [--offset N]
wgtl sites get <ID>
wgtl sites create --field K:V...      # e.g. hostname, root_page_id (required)
wgtl sites update <ID> --field K:V... [--yes]     # PUT: all required fields
wgtl sites delete <ID> [--yes]
```

## `wgtl locales`

Manage locales.

```
wgtl locales list [--limit N] [--offset N]
wgtl locales get <ID>
wgtl locales create --field K:V...    # e.g. language_code (required)
wgtl locales update <ID> --field K:V... [--yes]    # PUT: language_code required
wgtl locales delete <ID> [--yes]
```

## `wgtl redirects`

Manage redirects.

```
wgtl redirects list [--order F] [--limit N] [--offset N]
wgtl redirects find [--id N] [--path /old/]
wgtl redirects get <ID>
wgtl redirects create --field K:V...  # e.g. old_path (required)
wgtl redirects update <ID> --field K:V... [--yes]   # PUT: old_path required
wgtl redirects delete <ID> [--yes]
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