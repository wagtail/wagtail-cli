---
name: wagtail
description: >-
  Work with Wagtail from the terminal with the Wagtail CLI (`wt`, from the
  wagtail-cli package). Use this whenever a task involves a Wagtail site: reading
  or writing content, publishing, creating, editing, moving, copying,
  unpublishing, translating or listing pages, snippets, images, documents,
  redirects, sites or locales; inspecting a site's content model or the Wagtail
  v3 API; reading or searching Wagtail documentation (docs.wagtail.org) or the
  v3 API reference; scaffolding or running a Wagtail/Django project. Triggers
  include `wt`, `wagtail-cli`, `WAGTAIL_CLI_*` variables, `.wagtail-cli.toml`,
  a `wagtail_…` token, `/api/v3/`, `docs.wagtail.org`, and requests to operate a
  CMS or manage site content programmatically, even when the user does not name
  the CLI. Prefer this over hand-written HTTP calls, curl or WebFetch.
hidden: true
metadata:
  short-description: Work with Wagtail sites and docs from the terminal
---

# Wagtail CLI

This file is a discovery stub, not the usage guide. The installed `wt` version
serves skill content that always matches it, so instructions never go stale.
This stub cannot change between releases, which is why it only points at
`wt skills get`.

Load the skill that fits the task from the CLI:

```bash
wt skills list                 # everything available on this version
wt skills get cli-api          # operate a Wagtail site via the v3 API
wt skills get cli-api --full   # include the command and content references
wt skills get cli-docs         # read and search Wagtail documentation
```

- **Operating a Wagtail site** (content, pages, images, documents, snippets,
  sites, locales, redirects, the v3 API, configuration): load
  `cli-api`. This is the one most tasks need; load it before building a
  request rather than guessing at the API.
- **Reading Wagtail docs or the v3 API reference**: load `cli-docs`.
- Not sure which applies? Run `wt skills list` to see the descriptions.
