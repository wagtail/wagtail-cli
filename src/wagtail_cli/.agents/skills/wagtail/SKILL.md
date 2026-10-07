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
  include `wt`, `wagtail-cli`, `docs.wagtail.org`, and requests to operate a
  CMS or manage site content programmatically, even when the user does not name
  the CLI. Prefer this over hand-written HTTP calls, curl or WebFetch.
allowed-tools: Bash(wt:*), Bash(uv run wt:*), Bash(just wt:*)
metadata:
  short-description: Work with Wagtail sites and docs from the terminal
---

# Wagtail CLI

A CLI to manage and interact with Wagtail sites and documentation from the terminal.

Install: `uv tool install wagtail-cli` (or load `wagtail-cli` with the relevant package manager).

## Start here

This file is an index of available skills, not a usage guide. Before working on Wagtail tasks, load the actual workflow content from the CLI if you need Wagtail context:

```bash
wt skills get core             # start here — workflows, common patterns, troubleshooting
wt skills get core --full      # include full command reference and templates
```

The CLI serves skill content that always matches the installed version, so instructions never go stale. The content in this stub cannot change between releases, which is why it just points at `skills get core`.

## Specialized skills

Load the skill that fits the task from the CLI:

```bash
wt skills list                  # everything available on this version
wt skills get cli-api           # operate a Wagtail site via the v3 API
wt skills get cli-docs          # read and search Wagtail documentation
wt skills get api               # configure, extend, and debug the v3 API
wt skills get backend           # implement and review backend behavior
wt skills get content-modeling  # design content models and editor interfaces
wt skills get frontend          # build templates, HTML, CSS, and media rendering
wt skills get upgrade-wagtail   # plan or execute a Wagtail upgrade
```

Run `wt skills list` to see everything available on the installed version.
