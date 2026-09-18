# wagtail-cli

> A command-line client for the Wagtail v3 API

wagtail-cli is a command-line client for the [Wagtail](https://wagtail.org/)
v3 API. Install it, point it at a site's API, and your CMS is available from
the terminal — for local dev, live sites, and AI agents. `wt docs` puts
docs.wagtail.org in your terminal as Markdown.

This documentation covers installation, usage, and the package's internals.

## Features

- All Wagtail v3 API operations from one command: `pages`, `images`,
  `documents`, `snippets`, `sites`, `locales`, `redirects`, and `schema`,
  plus `wt api init` and `wt api whoami` for setup.
- Script-friendly conventions: JSON when piped and human-readable on a
  terminal, `--dry-run` on every mutating command, confirmation gates with
  `--yes`, and descriptive exit codes.
- Markdown-first content: rich-text fields accept Markdown via `.md` file
  references, sent to the API as `db_markdown`.
- **`wt docs`** — docs.wagtail.org as Markdown: release notes, the v3 API
  reference, and search. Needs no configuration at all.
- **`wt start`** — scaffold a new Django/Wagtail project.
- **Delegation** — any unknown `wt <command>` is forwarded to the current
  project's Django management runner, so `wt` also fronts Django commands
  like `wt runserver` and `wt makemigrations`.

## When to use it

Use `wt` to manage a Wagtail site without opening the admin: batch content
updates, content checks in CI, scripted publishing, or AI-orchestrated content
management. For example, publishing a blog post written in Markdown is one
command:

```bash
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Hello world" --field body:@post.md --publish
```

## Where to go next

- **New to `wt`?** Follow [Getting started](getting-started.md) to install it
  and publish your first page.
- **Looking up a command?** Browse the [command reference](usage.md) for every
  command and flag.
- **Scripting the CLI?** See [Configuration](reference/configuration.md) for
  the config cascade, and the [API reference](reference/api.md) built from the
  source docstrings.
- **Working with an agent?** See [Agent skills](agent-skills.md) for the
  machine-readable skill published with these docs.
- **Contributing?** Read the
  [contribution guidelines](https://github.com/wagtail/wagtail-cli/blob/main/docs/CONTRIBUTING.md)
  and the [development guide](contributing/development.md).

## License

wagtail-cli is licensed under the BSD-3-Clause license. See
[LICENSE](https://github.com/wagtail/wagtail-cli/blob/main/LICENSE) for
details.
