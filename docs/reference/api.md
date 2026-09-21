# API reference

This page is generated from the package's docstrings with
[mkdocstrings](https://mkdocstrings.com/). Update the source code, not this
page, when the API changes.

The CLI's user-facing interface is the `wt` command itself — see
[Usage](../usage.md) for the command reference. This page covers the Python
modules behind it.

## CLI

The root Typer application, the `api` command group, and the `cli()` entry
point handling delegation:

::: wagtail_cli.cli.main

## Configuration

The configuration cascade resolving flags, environment variables, and
dotfiles:

::: wagtail_cli.config

## Errors

The error hierarchy and exit-code mapping:

::: wagtail_cli.errors

## Output

JSON and human-readable rendering:

::: wagtail_cli.output

## Field parsing

`--field` value parsing, `@file` references, and page-ref resolution:

::: wagtail_cli.parsing

## Docs viewer

Resolving, fetching, and rendering docs.wagtail.org content for `wt docs`:

::: wagtail_cli.docs

## Transport

The HTTP client shared by all resources, with auth, error mapping, `--dry-run`
and `-v` support:

::: wagtail_cli.resources._client
