# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `wt docs` command: read docs.wagtail.org as Markdown from the terminal, in
  the style of the Stripe CLI docs viewer. `wt docs [PATH]` fetches a page
  (accepting full URLs, version-qualified paths, or bare page paths, with
  version detection from the locally installed Wagtail), `wt docs api`
  looks up v3 API reference operations, and `wt docs search` queries the
  site's search engine. The docs site can be overridden with `--docs-url` or
  `WAGTAIL_CLI_DOCS_URL`, e.g. to read docs from a PR build.

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
