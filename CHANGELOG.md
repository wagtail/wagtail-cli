# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `--select` is now accepted on every `api` command, not just globally, so
  `wt api sites list --select id,hostname` works. Global and command-local
  selectors are merged.
- `--json`, `--human`, and `--dry-run` are now accepted on every `api`
  command as well as globally, so `wt api pages list --json` and
  `wt api pages delete 42 --dry-run` work. A command-local flag overrides the
  global one.
- `wt api schema show` renders human-readable output with `--human` (JSON
  remains the default).
- New [documentation style guide](contributing/style-guide.md) for contributor and user-facing docs.
- Published a [JSON Schema for the dotfiles](https://wagtail.github.io/wagtail-cli/schema/wagtail-cli.json) (served from the docs site). Editors that understand the `#:schema` hint (Taplo, Even Better TOML, JetBrains) now complete and validate the keys in `.wagtail-cli.toml`. `wt api init` writes the hint automatically.

## [0.3.0] - 2026-09-22

- New [documentation website](https://wagtail.github.io/wagtail-cli/)
- New [agent skills for CLI features](https://wagtail.github.io/wagtail-cli/agent-skills/)
- Add `--select` response projections for more compact output.
- Output JSON errors when `--json` is selected.
- Add path-based `pages get` to combine page lookup and retrieval in one CLI invocation.
- Add `wt docs [PATH] --outline` to quickly check a page's structure.
- Support both global and command-local `--json` options for `wt docs search`.
- Better detect local projects when wagtail-cli is installed globally rather than in the same environment as the project.

## [0.2.0] - 2026-09-04

### Added

- `wt docs` command: read docs.wagtail.org as Markdown from the terminal.

## [0.1.1] - 2026-08-27

- Fix outdated `click` reference, prefer vendored `Context` instead.

## [0.1.0] - 2026-08-27

First release 🌈 Please share your feedback on our plans: [CMS with AI, not AI CMS: Wagtail 8.0’s new API](https://wagtail.org/blog/cms-with-ai-not-ai-cms-wagtail-80s-new-api/).


<!-- TEMPLATE - keep below to copy for new releases -->
<!--


## [x.y.z] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

-->
