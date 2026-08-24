# Command reference

`wt` is organized as a Typer app with one nested command group, `api` (all
Wagtail v3 API operations, including the setup commands `whoami` and `init`),
a `start` command that scaffolds a new Django/Wagtail project, and a
delegation rule: any command `wt` doesn't know is forwarded to the current
project's Django management runner.

## Global options

Available on `wt api` invocations (placed before `api` on the command line):

| Flag | Description |
|---|---|
| `--url URL` | API base URL (overrides config/env). |
| `--token TOKEN` | API token (overrides config/env). |
| `--json` | Force JSON output. |
| `--human` | Force human-readable output. |
| `-v` / `--verbose` | Print HTTP request/response details to stderr. |
| `--dry-run` | Print the request that would be sent, without sending it. |

`--json` and `--human` are mutually exclusive (the CLI exits with a usage
error if both are given).

Top-level `--version` and `--help` are handled by `wt` itself:

- `wt --version` prints the CLI version, plus the detected Wagtail and Django
  versions when those tools are available.
- `wt --help` prints this help, plus `./manage.py --help` when a `manage.py`
  exists in the current directory.

## Version and help

```bash
wt --version   # wagtail-cli <version>, plus Wagtail/Django when detected
wt --help      # CLI help, plus ./manage.py --help when present
```

## Delegation

Any `wt <command>` that is not `api`, `start`, `--version`, or `--help` is
delegated to the current project's Django management command runner, in this
order:

1. `./manage.py` if that file exists in the current directory;
2. `django-admin` if the `DJANGO_SETTINGS_MODULE` environment variable is set;
3. otherwise a clear error explaining that neither is available.

Delegation lets `wt` act as a swiss-army front end for Django commands
(`runserver`, `makemigrations`, `shell`, `check`, …) in an existing project:

```bash
wt runserver          # -> ./manage.py runserver
wt makemigrations     # -> ./manage.py makemigrations
wt shell              # -> ./manage.py shell
```

The remaining arguments (and flags) are passed through verbatim to the
delegated command.

## `wt start`

Scaffold a new Django/Wagtail project directory. This replicates the `start`
command of `wagtail` / Django's `django-admin startproject`, using the custom
base-page template by default.

```
wt start NAME [DIRECTORY]
```

Positional arguments:

| Arg | Description |
|---|---|
| `NAME` | Name of the application or project. |
| `DIRECTORY` | Optional destination directory, created if needed. |

Options (all override the defaults, which mirror `wagtail start`):

| Option | Description |
|---|---|
| `--template TEMPLATE` | Path or URL to load the template from (default: the custom base-page template). |
| `-e, --extension EXT` | File extension(s) to render (default: `html,rst`, repeatable). |
| `-n, --name FILE` | File name(s) to render (default: `Dockerfile`, repeatable). |
| `-x, --exclude [DIR]` | Directory name(s) to exclude, in addition to `.git` and `__pycache__` (repeatable). |
| `-v, --verbosity {0,1,2,3}` | Verbosity level. |
| `--settings SETTINGS` | Python path to a settings module. |
| `--pythonpath PYTHONPATH` | Directory to add to the Python path. |
| `--traceback` | Display a full stack trace on `CommandError`. |
| `--no-color` | Don't colorize the command output. |
| `--force-color` | Force colorization of the command output. |
| `--version` | Show Django's `startproject` version and exit. |

`wt start` requires `django-admin` on `PATH` (it shells out to
`django-admin startproject`, since `wt` itself does not depend on Django).

```bash
wt start myproject                    # default custom template
wt start myproject ./site --template https://example.com/tmpl.zip -e py -e html
```

---

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

## `wt api whoami`

Print the authenticated user, profile, and groups.

## `wt api init`

Interactive setup: prompts for URL + token (unless both flags are given),
tests the connection, and writes `~/.wagtail-cli.toml`.

## `wt api schema`

Discover the content model.

```
wt api schema list
wt api schema show <TYPE>       # e.g. blog.BlogPage — raw JSON schema
```

## `wt api pages`

Read, create, and manage pages, including actions and revisions.

```
wt api pages list [--type T]* [--child-of REF] [--descendant-of REF]
                [--ancestor-of REF] [--translation-of N] [--locale CODE] [--site N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt api pages find [--id N] [--path /blog/] [--site N]
wt api pages get <ID> [--version draft|live] [--html]
wt api pages create <TYPE> --parent REF --title T
                [--slug S] [--field K:V]... [--publish]
wt api pages update <ID> [--title T] [--slug S] [--field K:V]... [--publish] [--yes]
wt api pages delete <ID> [--yes]
wt api pages publish <ID>
wt api pages unpublish <ID>
wt api pages copy <ID> --destination REF [--slug S] [--title T]
                [--recursive/--no-recursive] [--keep-live/--no-keep-live]
wt api pages move <ID> --destination REF
wt api pages revert <ID> --revision N
wt api pages create-alias <ID> --destination REF
wt api pages convert-alias <ID>
wt api pages copy-for-translation <ID> --locale CODE
wt api pages revisions list <ID> [--limit N] [--offset N]
wt api pages revisions get <ID> <REVISION_ID>
```

`REF` is a page id or a URL path (e.g. `/blog/`), resolved through the API's
find endpoint. `--field` values that start with `[` or `{` are parsed as JSON;
`@file` reads a value from a file (`@-` = stdin). Multi-line rich-text bodies
read from a `.md` file are sent with `format: db_markdown`.

## `wt api images`

Upload and manage images.

```
wt api images list [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt api images get <ID>
wt api images create <FILE> --title T [--field K:V]...     # multipart upload
wt api images update <ID> [--title T] [--field K:V]... [--yes]
wt api images delete <ID> [--yes]
```

## `wt api documents`

Upload and manage documents.

```
wt api documents list [--search Q] [--search-operator and|or] [--order F]
                   [--limit N] [--offset N]
wt api documents get <ID>
wt api documents create <FILE> --title T [--field K:V]...  # multipart upload
wt api documents update <ID> [--title T] [--field K:V]... [--yes]
wt api documents delete <ID> [--yes]
```

## `wt api snippets`

Manage API-enabled snippets. The snippet type is always required (each snippet
model lives in its own table).

```
wt api snippets list <TYPE> [--locale CODE] [--translation-of N]
                [--search Q] [--search-operator and|or] [--order F]
                [--limit N] [--offset N]
wt api snippets get <TYPE> <PK>
wt api snippets create <TYPE> [--field K:V]...
wt api snippets update <TYPE> <PK> [--field K:V]... [--yes]
wt api snippets delete <TYPE> <PK> [--yes]
wt api snippets publish <TYPE> <PK>
wt api snippets unpublish <TYPE> <PK>
wt api snippets revert <TYPE> <PK> --revision N
wt api snippets copy-for-translation <TYPE> <PK> --locale CODE
wt api snippets revisions list <TYPE> <PK> [--limit N] [--offset N]
wt api snippets revisions get <TYPE> <PK> <REVISION_ID>
```

## `wt api sites`

Manage sites.

```
wt api sites list [--limit N] [--offset N]
wt api sites get <ID>
wt api sites create --field K:V...      # e.g. hostname, root_page_id (required)
wt api sites update <ID> --field K:V... [--yes]     # PUT: all required fields
wt api sites delete <ID> [--yes]
```

## `wt api locales`

Manage locales.

```
wt api locales list [--limit N] [--offset N]
wt api locales get <ID>
wt api locales create --field K:V...    # e.g. language_code (required)
wt api locales update <ID> --field K:V... [--yes]    # PUT: language_code required
wt api locales delete <ID> [--yes]
```

## `wt api redirects`

Manage redirects.

```
wt api redirects list [--order F] [--limit N] [--offset N]
wt api redirects find [--id N] [--path /old/]
wt api redirects get <ID>
wt api redirects create --field K:V...  # e.g. old_path (required)
wt api redirects update <ID> --field K:V... [--yes]   # PUT: old_path required
wt api redirects delete <ID> [--yes]
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
wt --dry-run api pages publish 42
wt api pages delete 42 --yes
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