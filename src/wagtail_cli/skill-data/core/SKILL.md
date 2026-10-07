---
name: core
description: Core documentation and orientation for work on Wagtail projects. Use for Wagtail questions, planning, implementation, or debugging; load specialized Wagtail skills on demand for the aspect being changed.
metadata:
  short-description: Core documentation and orientation for work on Wagtail projects.
---

# Wagtail core

Use this as the starting point for Wagtail work. Read documentation and load specialized guidance as the task requires.

## Establish the project context

Identify the project's Wagtail and Django versions from installed packages or dependency files. Follow its existing models, settings, templates, and extension patterns when deciding how Wagtail fits the requested change.

Use documentation for that Wagtail release: replace `stable` in the links below with its documentation version. `stable` follows the current release; `latest` may describe unreleased behavior. If documentation is unavailable or differs from runtime behavior, inspect the matching installed source and tests.

## Find the relevant documentation

Note: if available, use the `cli-docs` skill to access Wagtail documentation directly from the CLI. Run `wt skills get cli-docs` to load it.

Start with the [documentation index](https://docs.wagtail.org/llms.txt) to locate pages for the task. Prefer `.html.md` versions for reading developer documentation; use the HTML URLs when linking documentation for the user. Read the relevant pages rather than loading the whole manual.

- [Wagtail documentation](https://docs.wagtail.org/en/stable/index.html): entry point for usage guides, API references, deployment, and release notes.
- [The Zen of Wagtail](https://docs.wagtail.org/en/stable/getting_started/the_zen_of_wagtail.html): Wagtail's approach to content, editors, and developer control.
- [Page models](https://docs.wagtail.org/en/stable/topics/pages.html): the foundation for content types, the page tree, and page rendering.
- [Model reference](https://docs.wagtail.org/en/stable/reference/models.html): pages, sites, revisions, and other core model contracts.
- [Editor’s guide](https://guide.wagtail.org/): understand the editorial experience when work affects how people manage content.

For behavior outside Wagtail, consult the matching [Django documentation](https://docs.djangoproject.com/en/stable/). For changes to Wagtail itself, use its [contributing documentation](https://docs.wagtail.org/en/stable/contributing/index.html) and the repository's contributor instructions.

## Answer questions about using the CMS

Use the [Wagtail User Guide](https://guide.wagtail.org/) as the primary source for questions from editors, moderators, and administrators about using the CMS. This includes finding content, managing pages and media, publishing and scheduling, moderation workflows, permissions, and account settings. Keep in mind that the guide may not reflect customizations or extensions present in the user's specific Wagtail installation.

- Find relevant pages through the guide's navigation, search, or [llms.txt index](https://guide.wagtail.org/llms.txt). Use a page's “View page Markdown” link when available to read its content; link the ordinary page URL in answers.
- Use how-to guides for steps to complete a task, concepts and reference pages to explain CMS behavior, and user release notes for changes to the editorial experience.
- Check whether the described feature applies to the user's Wagtail version. Use release notes or matching developer documentation to resolve version differences; do not assume the current guide matches an older installation.
- Explain steps using the guide's interface labels. Account for the user's role and the site's customizations: available controls, page types, and workflows can differ from the standard interface. State relevant assumptions when these details are unknown.

When the question requires implementing or customizing CMS behavior, supplement the User Guide with developer documentation and the relevant specialized skill.

## Load specialized skills on demand

When a task reaches one of these areas, load the corresponding skill from the agent's available skill inventory. Load only those relevant to the requested work; a task may need more than one.

### General utility skills

For day-to-day operations and interactions with a Wagtail project, the following general utility skills are useful:

- `cli-api`: Operate a Wagtail site via its API, with the Wagtail CLI.
- `cli-docs`: Read and search Wagtail documentation from the terminal, faster than web fetching.

### Specialized project skills

For specific areas of expertise within a Wagtail project:

- `content-modeling`: Work with page types, snippets, settings, fields, StreamField, and editor panels.
- `backend`: Work with queries, routing, search, permissions, revisions, workflows, forms, and runtime performance.
- `frontend`: Work with templates, rich text and block rendering, images, accessibility, metadata, and frontend performance.
- `api`: Work with configuring, extending, consuming, or debugging Wagtail's v3 API.
- `upgrade-wagtail`: Work with planning or executing a Wagtail upgrade, or extending a package's supported Wagtail versions.

If a relevant skill is unavailable, continue with the version-matched official documentation.
