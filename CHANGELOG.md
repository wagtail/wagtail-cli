# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
