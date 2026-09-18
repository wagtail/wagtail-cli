---
name: wagtail-cli
description: Drive a Wagtail site's v3 API from the terminal with the wt command-line client. Use this skill when reading or changing CMS content (pages, images, documents, snippets, sites, locales, redirects), scaffolding a Wagtail project, reading Wagtail docs, or running Django management commands through wt delegation.
---

# wagtail-cli

Instructions for using `wt`, the command-line client for the Wagtail v3 API,
to manage CMS content reliably from an agent or script.

## When to use this skill

- Read or change content on a Wagtail site: pages, images, documents,
  snippets, sites, locales, redirects.
- Discover a site's content model before creating or updating content.
- Scaffold a new Django/Wagtail project (`wt start`).
- Read Wagtail documentation or the v3 API reference in the terminal (`wt docs`).
- Run Django management commands in an existing project via delegation
  (`wt runserver`, `wt makemigrations`).

## Setup

1. Check the CLI is available: `wt --version`. Install with
   `uv tool install wagtail-cli` if missing.
2. Get an API base URL and token. Configure with environment variables
   (`WAGTAIL_CLI_BASE_URL`, `WAGTAIL_CLI_TOKEN`) or run `wt api init` once to
   write `~/.wagtail-cli.toml`. Flags `--url` / `--token` override per call.
3. Verify credentials: `wt api whoami`. A 401 or 403 exit code means the token
   is wrong or lacks permission — stop and ask for a working token rather than
   retrying.

## Workflow for content tasks

1. **Discover the content model first**: `wt api schema list`, then
   `wt api schema show <type>` for the exact fields of a page or snippet type.
2. **Find the target**: `wt api pages list --search "…"`,
   `wt api pages find --path /blog/`, or list with `--type` filters.
3. **Dry-run every mutation**: mutating commands accept `--dry-run`, which
   prints the exact request without sending it. Run it, check the payload,
   then run again without `--dry-run`.
4. **Create or update with `--field key:value`**:
   - Values starting with `[` or `{` are parsed as JSON.
   - `@path` reads a value from a file, `@-` from stdin; a `.md` file is sent
     as `db_markdown` rich text, a `.json` file as parsed JSON.
   - Create page drafts without `--publish`; add `--publish` to make them live.
5. **Confirm destructive commands**: on non-interactive runs, `update` and
   `delete` require `--yes`; they never prompt when piped.
6. **Verify the result**: `wt api pages get <ID> --version live`.

## Rules for reliable output

- Always pass `--json` when another tool parses the output; human tables are
  for terminals only. `-v` logs HTTP traffic to stderr, not stdout.
- Exit codes are meaningful: 0 success, 2 usage error, 3 network error, 4 auth
  error (401), 5 permission (403), 6 not found (404), 7 validation
  (400/422). Check the exit code before parsing stdout.
- Errors print an RFC 7807 problem body to stderr — surface it verbatim when
  reporting failures.
- Actions (`publish`, `unpublish`, `revert`, `copy-for-translation`) run
  immediately without confirmation — always preview with `--dry-run` first.

## Reference

- Command reference: <https://wagtail.github.io/wagtail-cli/usage/>
- Configuration precedence (flags > env > project dotfile > user dotfile):
  <https://wagtail.github.io/wagtail-cli/reference/configuration/>
- Full docs digest for LLMs: <https://wagtail.github.io/wagtail-cli/llms-full.txt>
