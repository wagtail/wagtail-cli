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

- The demo site now runs Django 6.1 and Wagtail 8.0. Supporting this requires Python 3.12+, so the package's minimum supported Python version is raised from 3.11 to 3.12.
- Migrate the demo site's `EMAIL_BACKEND` setting to `MAILERS`, deprecated in Django 6.1.

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
