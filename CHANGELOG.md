# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- MkDocs documentation site (Material theme), published to GitHub Pages on every push to `main`. Build locally with `just docs-build` / `just docs-serve`.
- LLM-friendly docs output: `llms.txt` and `llms-full.txt` digests at the site root, via `mkdocs-llmstxt`.
- Agent skills discovery: the docs publish the package's agent skill under `.well-known/agent-skills/`, with machine-readable indexes at `.well-known/agent-skills/index.json` and `.well-known/ai-catalog.json`.

### Changed

- Support both global and command-local `--json` options for `wt docs search`.
- Split the `wagtail-cli` agent skill into `wagtail-api` and `wagtail-docs`. `wagtail-api` is rewritten from evaluated runs against the demo site: a short `SKILL.md` focused on configuration, gotchas and a reporting default, with `references/commands.md` and `references/writing-content.md` for the full command surface and content payloads. `wagtail-docs` is a few lines on `wt docs` so agents stop fetching docs.wagtail.org pages by hand. The docs build now publishes each skill directory, not just `SKILL.md`, and the skills are bundled in the wheel and sdist under `wagtail_cli/.agents/skills/`.
- Demo site: declare the blog and person API fields as writable so the v3 API accepts content writes.
- The demo site now runs Django 6.1 and Wagtail 8.0. Supporting this requires Python 3.12+, so the package's minimum supported Python version is raised from 3.11 to 3.12.
- Migrate the demo site's `EMAIL_BACKEND` setting to `MAILERS`, deprecated in Django 6.1.

### Fixed

- Delegated Django commands (for example `wt runserver` with a `manage.py` in the current directory) now run with the project's own interpreter rather than the one `wt` is installed in. This fixes running `wt` from an isolated install (`uv tool install wagtail-cli`, pipx), where Django is not available: the CLI resolves the active `$VIRTUAL_ENV` or a `.venv` / `venv` directory in the current directory, and prints a hint when it still cannot find a suitable interpreter. The `DJANGO_SETTINGS_MODULE` fallback now prefers `python -m django` with the resolved interpreter over a PATH `django-admin`.
- `wt --version` and `wt --help` detect the project's Wagtail and Django versions through the project's interpreter, so isolated installs report the versions of the site being worked on rather than coming up empty.
- `wt docs` resolves the default docs version from the project's Wagtail installation when Wagtail is not installed alongside `wt`, falling back to `stable` only when no project Wagtail can be found.

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
