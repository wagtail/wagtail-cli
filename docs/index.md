# Wagtail CLI

> Speed up and automate Wagtail operations with the command line.

The Wagtail CLI provides tools to speed up your work with [Wagtail](https://wagtail.org/) and Django. Its flagship is a client for Wagtail’s v3 API, to automate CMS operations. Install it, point it at a site's API, and your CMS is available from the terminal. for local dev, live sites, and AI agents.

It also comes with [Agent Skills](https://agentskills.io/) and documentation fetching for agents, to speed up all Wagtail tasks. This is implemented with progressive disclosure to not pollute your context unless you’re working on Wagtail tasks.

---

This documentation covers installation, usage, and the package's internals.

## Features

- **`wt api`**: All Wagtail v3 API operations from one command: `pages`, `images`, `documents`, `snippets`, `sites`, `locales`, `redirects`, and `schema`, plus `wt api init` and `wt api whoami` for setup.
- **`wt skills`**: Self-loading Wagtail expert skills for agents across a broad range of tasks.
- **`wt docs`**: docs.wagtail.org as Markdown: release notes, the v3 API reference, and search. Needs no configuration at all.
- **`wt start`**: scaffold a new Django/Wagtail project.
- **Delegation**: any unknown `wt <command>` is forwarded to the current project's Django management runner, so `wt` also fronts Django commands like `wt runserver` and `wt makemigrations`.

Here’s an example, helping your agent to create a blog post with three steps:

```bash
# Learn about how the CLI API client works.
wt skills get cli-api
# Discover the site’s data model for blog pages.
wt docs api GET /api/v3/schema/blog.BlogPage/
# Create a new blog post using the discovered schema.
wt api pages create blog.BlogPage --parent /blog/ \
  --title "Hello world" --field body:@post.md --publish
```

## Where to go next

- [Getting started](getting-started.md) to install it and publish your first page.
- **Looking up a command?** Browse the [command reference](usage.md) for every command and flag.
- **Scripting the CLI?** See [Configuration](reference/configuration.md) for the config cascade, and the [API reference](reference/api.md) built from the source docstrings.
- **Working with an agent?** See [Agent skills](agent-skills.md) for the machine-readable skill published with these docs.
- **Contributing?** Read the [contribution guidelines](CONTRIBUTING.md) and the [development guide](contributing/development.md), and follow the [documentation style guide](contributing/style-guide.md) when writing docs.

## License

wagtail-cli is licensed under the BSD-3-Clause license. See [LICENSE](https://github.com/wagtail/wagtail-cli/blob/main/LICENSE) for details.
