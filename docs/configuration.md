# Configuration

The CLI needs a base URL and an API token. Provide them via flags, environment
variables, dotfiles, or `wt api init`.

## Precedence

Settings are resolved from highest to lowest priority:

| Priority | Source | Example |
|---|---|---|
| 1 (highest) | CLI flags | `--url`, `--token` |
| 2 | Environment variables | `WAGTAIL_CLI_BASE_URL`, `WAGTAIL_CLI_TOKEN` |
| 3 | Project dotfile | `./.wagtail-cli.toml` |
| 4 (lowest) | User dotfile | `~/.wagtail-cli.toml` |

Each key (`url`, `token`) resolves independently across the cascade — the
highest source that *defines that key* wins. A project dotfile can set `url`
while the environment sets `token`; both apply.

## Environment variables

```bash
export WAGTAIL_CLI_BASE_URL="https://cms.example.com/api/v3/"
export WAGTAIL_CLI_TOKEN="wagtail_abc123def456"
```

Setting these (or the dotfiles) is all you need for scripts and CI. `--url`
and `--token` flags override them for a single invocation.

## Dotfiles

`wt api init` writes the user dotfile interactively:

```bash
wt api init
# API base URL: https://cms.example.com/api/v3/
# API token: ****************************
# Testing connection… ✓
# Wrote ~/.wagtail-cli.toml
```

If `--url` and `--token` are both given, `init` skips the prompts.

The project dotfile lives at `./.wagtail-cli.toml` in the current working directory
and overrides the user dotfile — useful for per-repo configuration committed
to a shared team setup (though avoid committing real tokens).

```toml
# ~/.wagtail-cli.toml or ./.wagtail-cli.toml
url = "https://cms.example.com/api/v3/"
token = "wagtail_abc123def456"
```

> Do not commit production tokens. The project dotfile is intended for shared
> URLs or dev-only tokens; use environment variables or the user dotfile for
> real credentials.