# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `wt`, a CLI client for the Wagtail v3 API, with full coverage of the
  shipped OpenAPI operations: pages (CRUD, find, publish/unpublish, copy, move,
  revert, aliases, copy-for-translation, revisions), images, documents,
  snippets (incl. actions and revisions), sites, locales, redirects, schema, and
  whoami.
- CLI contract: a config cascade (flags → env → project dotfile → user
  dotfile), JSON-when-piped output with `--json`/`--human` overrides,
  `--dry-run` on mutating commands, RFC 7807 error forwarding, and stable
  exit codes.
- Content ergonomics: repeatable `--field KEY:VALUE` with JSON auto-parse and
  `@file`/`@-`/stdin readers, plus `.md` → `db_markdown` rich-text envelopes.
- Client generated from the OpenAPI schema (`just generate-client`), an
  openapi snapshot, and a coverage-gap test guarding endpoint coverage.
- Unit tests for the CLI and resources layers (CliRunner + respx) and an
  opt-in integration suite for a live site.
- `wt start` scaffolds a Django project from the custom base-page template,
  mirroring `wagtail start` defaults.
- Unknown commands delegate to `./manage.py` (or `django-admin` when
  `DJANGO_SETTINGS_MODULE` is set).

### Changed

- Renamed the package to `wagtail-cli` (module `wagtail_cli`), command `wgtl` → `wt`.
- All API commands moved under `wt api` (including `wt api init` and `wt api whoami`).
- Config dotfile `~/.wgtl.toml` → `~/.wagtail-cli.toml`; env vars `WAGTAIL_*` → `WAGTAIL_CLI_*`.

## [0.1.0] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

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
