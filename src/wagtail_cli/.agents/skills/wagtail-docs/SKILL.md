---
name: wagtail-docs
description: >-
  Use when the user or agent needs to read, search, or look up Wagtail
  documentation or the Wagtail v3 API reference. Prefer this over curl or
  WebFetch for any docs.wagtail.org content, and over guessing how a Wagtail
  feature, setting, model, hook or API endpoint works.
metadata:
  short-description: Read and search the Wagtail documentation from the terminal
allowed-tools:
  - Bash(wt docs *)
  - Bash(wt --version)
---

Use `wt docs` instead of fetching [docs.wagtail.org](https://docs.wagtail.org/)
with `curl` or `WebFetch`. It prints pages as Markdown, needs no configuration
or credentials, and defaults to the docs for the locally installed Wagtail
version (falling back to `stable`). If `wt` is missing, install it with
`uv tool install wagtail-cli`.

## Read a page by its docs path

```bash
wt docs topics/pages                  # path as it appears in the docs index
wt docs releases/8.0                  # release notes
wt docs https://docs.wagtail.org/en/latest/topics/streamfield.html
```

`wt docs` with no path prints the table of contents, one path per line.
Pages can be long: pipe through `head` or `grep -A` when you need one section.

## Search by keyword

```bash
wt docs search "custom base page models"
```

Results show title, path and a snippet; read the page you want with the path.

## Look up the v3 API reference

```bash
wt docs api                           # index of every operation
wt docs api "POST /pages/"            # one operation, exact
wt docs api get documents             # method and /api/v3/ prefix optional
```

Project-specific endpoints are not in this reference; they only exist in
that project's own `<API root>/docs/`.

## Pin a version

```bash
wt docs --version 7.2 topics/images
wt docs --version latest search "workflows"
```
