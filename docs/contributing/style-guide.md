# Documentation style guide

This style guide defines the standard we aim for across wagtail-cli documentation — the README, the [MkDocs site](https://wagtail.github.io/wagtail-cli/), contributor docs, agent skills, and everything else. Use it as the default for all new content, and as a reference when revising existing pages.

Two audiences read this documentation, and the split shapes almost every rule below:

- **Users of the CLI** read the published site: [Getting started](../getting-started.md), the [command reference](../usage.md), [Configuration](../reference/configuration.md), the [API reference](../reference/api.md), and [Agent skills](../agent-skills.md). They have a Wagtail site and want to automate it.
- **Contributors** read the docs in [`docs/`](https://github.com/wagtail/wagtail-cli/tree/main/docs) on GitHub: [Contributing guidelines](../CONTRIBUTING.md), [Design principles](design-principles.md), the [development guide](development.md), [Skill evals](../evals/README.md), the [roadmap](../ROADMAP.md), and the [changelog](../CHANGELOG.md). They work on the package itself.

Keep the two apart. User-facing pages explain what `wt` does and how to use it; they don't mention internal modules or test layout. Contributor pages explain how the package is built and tested; they can point into the source but shouldn't restate command usage that already lives in the reference.

## Design goals

- **Accurate, discoverable, maintainable.** Docs should describe the CLI as it is, be easy to find, and be cheap to keep up to date.
- **Concise and practical.** Get to the point quickly. Prefer concrete examples over long prose explanations. Every page should help the reader accomplish something or understand a concept they need.
- **Users first.** When in doubt about order or depth, optimize for someone trying to use `wt`, following the priority order in the [design principles](design-principles.md#vision).

## Tone of voice

We write in a **direct, professional, and approachable** tone. The guiding principle: help the reader move forward with as little friction as possible.

- Contractions are acceptable where they read naturally: "doesn't", "won't", "It's", "That's", "Don't". Do not force them, and do not avoid them.
- Avoid overly formal or academic phrasing. Sentences stay direct and plain. Prefer "use" over "utilise", "start" over "commence", "show" over "demonstrate" (except where "demonstrate" is the precise word).
- Be honest about the project's maturity and limitations. The CLI is an early-stage prototype; say so where it matters (see [Warnings, notes, and edge cases](#warnings-notes-and-edge-cases)).

## Target audience

Write for the audience of the page you are editing.

- **User-facing pages** assume a Wagtail site with the v3 API enabled, and comfort with the command line. They do not assume familiarity with the CLI's internals or with Python packaging. Link out to Wagtail docs (for example `wt docs` or [docs.wagtail.org](https://docs.wagtail.org/)) rather than re-explaining Wagtail concepts.
- **Contributor pages** assume familiarity with the project's development tooling (`uv`, `just`, `mkdocs`, `prek`). Link to those tools' documentation rather than re-explaining them.
- Where a page mixes both — [Agent skills](../agent-skills.md) is mostly for users but links to [Skill evals](../evals/README.md) for contributors — keep the user-facing part first and clearly separated.

## Content structure

### Page layout

Every page follows a predictable shape:

1. **H1 page title** – concise, descriptive, in sentence case.
2. **Opening paragraph** – one or two sentences that tell the reader what the page covers and whether they are in the right place.
3. **Sections** – H2 for major sections, H3 for sub-sections within an H2. Use H4 and below sparingly; if a section needs five levels, consider splitting the page.

Task-oriented pages lead with the happy path: install, configure, do the thing. Reference pages (`usage.md`, `reference/configuration.md`) lead with a one-line description of the scope, then go straight into the tables or command list.

### Code examples

- Code blocks use fenced syntax (` ``` `) with a language identifier: `sh`, `bash`, `txt`, `markdown`.
- Examples should be self-contained where possible: a reader should be able to copy, paste, and run them. Prefer real-looking placeholders (`https://cms.example.com/api/v3/`, `wagtail_xxxx`) over `<your-url>` style stubs.
- Use `wt` commands with the global flags first — `wt --json api pages list`, not `wt api pages list --json` — matching how the CLI actually parses them.
- Inline comments inside code blocks are acceptable when they clarify non-obvious lines, but keep them short. Match the comment style used in the surrounding codebase (see the [development guide](development.md)).
- Prefer showing the happy path first. Document edge cases, fallbacks, and advanced configuration in a separate sub-section or callout.

### Tables

- Use Markdown tables for structured reference data: global options, exit codes, the configuration cascade, command groups, and agent-skill lookups.
- Every column should have a header row.
- Keep table cells short. If a cell needs a paragraph of explanation, move it into prose below the table.

### Callouts and blockquotes

We use Markdown blockquotes for short, scoped callouts:

- **Draft or status notes** at the top of a page:

  ```markdown
  > 🚧 This is a prototype. Feedback very welcome!
  ```

- **Constraints that change how the reader proceeds**, for example the install note in [Getting started](../getting-started.md):

  ```markdown
  > `wt` installed in isolation (uv tool, pipx) runs outside your project's
  > environment. Delegated Django commands automatically prefer your project's
  > interpreter.
  ```

- **Security or safety notes**, for example the "do not commit production tokens" warning in [Configuration](../reference/configuration.md#dotfiles).

- **Closing remarks** at the end of a procedure:

  ```markdown
  > Run `just lint` and `just test` before opening a pull request.
  ```

Keep callouts to one or two sentences. Use them when the information directly affects how the reader proceeds, not as a general aside.

For callouts that really do need to stand out, use MkDocs admonition syntax (`!!! note`, `!!! warning`). Admonitions are rendered on the published site but show literally on GitHub, so reserve them for pages that primarily live on the site. Blockquotes work everywhere and are the safer default.

## Links

- Use **inline links** in prose. Prefer `[link text](url)` over bare URLs.
- Link to internal documentation with **relative paths** to the target file: `[command reference](../usage.md)`, `[development guide](development.md)`. Always include the `.md` file in the path — links to folders work on GitHub but are left broken on the built site.
- To link to a section of a page, append its anchor: the heading text lowercased, spaces replaced with hyphens, punctuation removed. For example, `[Links](#links)`. `just docs-build` runs MkDocs in `--strict` mode and fails on broken internal links and anchors, so it catches mistakes before they ship.
- **User-facing pages** link to the features' canonical docs: [docs.wagtail.org](https://docs.wagtail.org/) for Wagtail, and the CLI's own pages on the site. Prefer a `wt docs` command in examples over a raw docs URL where one exists.
- **Contributor pages** can link directly into the repository: source modules under `src/wagtail_cli/`, tests under `tests/`, and workflow files under `.github/workflows/`.
- For GitHub issues and pull requests, use the shorthand from the `pymdownx.magiclink` extension: `wagtail/wagtail-cli#123` and `wagtail/roadmap#230` render as linked references.
- On first or prominent mention of a key concept, tool, or external resource, link to its canonical source. Repeat links only when the repetition genuinely helps scanning in a longer section.
- External links should point to **official, stable resources**: [wagtail.org](https://wagtail.org/), [docs.wagtail.org](https://docs.wagtail.org/), [PyPI](https://pypi.org/project/wagtail-cli/), [the Wagtail repository](https://github.com/wagtail/wagtail), and official tool documentation ([uv](https://docs.astral.sh/uv/), [Typer](https://typer.tiangolo.com/), [MkDocs](https://www.mkdocs.org/)). Avoid linking to transient content (forum threads, personal gists) unless there is no canonical alternative.
- Link text should be descriptive. Avoid "click here" or "this link". Prefer the title of the target page.
- Do not add links inside headings. They are harder to identify for screen reader users and break heading navigation.

### Frequently linked resources

Use these canonical URLs for resources we link often, so links stay consistent and are cheap to update:

| Resource              | URL                                              |
| :-------------------- | :----------------------------------------------- |
| Wagtail project       | https://wagtail.org/                             |
| Wagtail documentation | https://docs.wagtail.org/                        |
| Wagtail repository    | https://github.com/wagtail/wagtail               |
| wagtail-cli on PyPI   | https://pypi.org/project/wagtail-cli/            |
| wagtail-cli repository | https://github.com/wagtail/wagtail-cli          |
| Wagtail roadmap       | https://github.com/wagtail/roadmap               |
| Agent skills spec     | https://agentskills.io/                          |

## Headings and titles

- **H1** is used exactly once per page, for the page title.
- **H2** is the primary sectioning level within a page.
- **H3** is used for sub-sections within an H2. Use deeper levels only when the content genuinely requires it.
- Headings use **sentence case**: "Getting started", "Command reference", "Skill evals", not "Getting Started" or "Command Reference".
- Heading text is **plain**. Do not apply bold, italics, code formatting, or links inside headings.
- Prefer **noun phrases** for reference and conceptual pages ("Command reference", "Configuration", "Design principles"). Prefer **verb-first phrasing** for task-oriented pages or sub-sections within procedures ("Publish a page", "Regenerate the client", "Adding a command").
- Keep headings concise. A heading should fit on a single line and give the reader enough context to decide whether to read the section.

## Terminology and language choices

### Spelling

We use **American English** spelling in prose: `normalization`, `organized`, `behavior`, `color`, `center`. This is consistent with the spelling used in Wagtail's own documentation.

Exceptions:

- **Proper nouns and product names** keep their own spelling regardless of locale.
- When a prose sentence refers to a specific code symbol, use the symbol's exact spelling.
- Commands and flags are reproduced verbatim, including any hyphens: `wt api pages create`, `--dry-run`, `--no-recursive`.

### Capitalization

- **Sentence case** for headings and titles, always.
- Capitalize proper nouns: Wagtail, Django, Python, PyPI, Markdown, MkDocs, Typer, Prettier, Ruff, GitHub Actions, TensorX.
- The CLI's command is **`wt`**, lowercase, in code formatting. The package is **wagtail-cli**; the distribution on PyPI is `wagtail-cli`.
- **"this project"** is acceptable in contributor docs; **"the CLI"** or **`wt`** is preferred in user-facing docs.
- "the demo site" / "the demo project" refers to the Wagtail site in `demo/`. It is lowercase — it is not a proper noun.
- Environment variables and config keys are written in code formatting with their exact case: `WAGTAIL_CLI_BASE_URL`, `WAGTAIL_CLI_TOKEN`, `WAGTAIL_CLI_DOCS_URL`.

### Punctuation

- Use an **en dash** (`–`) with surrounding spaces as a separator in lists and inline definitions, matching the existing docs:

  ```markdown
  - **Unit, CLI layer** – Typer `CliRunner` + respx.
  - **Coverage gap** – asserts every operation maps to a CLI command.
  ```

- Use a **colon** before a code block or list that the preceding sentence introduces: "Errors print `Error (status): message` plus the RFC 7807 body to stderr."
- **Hard-wrap prose at around 80 characters** rather than putting a whole paragraph on one source line. Every existing page does this; keeping to it makes diffs and GitHub review readable, and lets a paragraph be read at a comfortable line length on wide screens. Wrap at a word boundary — never break a code span, link, or URL mid-token, and let an over-long token overflow on its own line if it must. Tables, fenced code blocks, and front matter are exempt.
- Comments in code blocks follow the same rule as source code: avoid hard-wrapping, except at full stops or other natural punctuation breaks.

### Referring to the reader

- We say "you" and "your". We do not say "the user" when addressing the reader of the documentation.
- "Users", "contributors", and "agents" refer to other people (or tools) rather than the reader: "users of the CLI", "contributors to the package", "AI agents".
- For the CLI's own input/output description, "the user" is fine when it is the CLI talking about an authenticated account (`wt api whoami` prints the authenticated user).

### Referring to the project and its parts

- "`wt`" – the command-line interface, in code formatting. Use it instead of "wagtail-cli" when describing commands.
- "the CLI" – acceptable prose shorthand for `wt` after first mention.
- "wagtail-cli" – the package name, in prose without code formatting.
- "Wagtail" – the open source CMS. Always capitalized.
- "the v3 API" – the Wagtail API version the CLI targets (Wagtail 8.0+). Spell it out on first mention: "the Wagtail v3 API".
- "the demo site" – the Wagtail site in `demo/` used for development and examples.
- "docs.wagtail.org" – lowercase URL form when referring to the Wagtail documentation site. Do not capitalize the domain.
- "agent skills" – the machine-readable skills bundled with the package (see [Agent skills](../agent-skills.md)). Lowercase except in a title.

### CLI terminology

- **global flags** – flags placed before the subcommand (`wt --json api pages list`). Say so explicitly when the placement matters.
- **command group** – a nested group such as `wt api` or `wt docs`.
- **delegation** – forwarding an unknown `wt <command>` to `./manage.py` or `django-admin`.
- **`--field`** – the repeatable key/value flag for content fields. Describe value forms (`@file`, `@-`, JSON prefixes) precisely; these are easy to get wrong.
- **exit codes** – refer to them in prose as "exit 0", "exit 2", and so on. The [exit code table](../usage.md#exit-codes) is the canonical list.
- **dotfile** – `.wagtail-cli.toml` in the project or home directory. Use "project dotfile" and "user dotfile" as in [Configuration](../reference/configuration.md#dotfiles).

### Modal verbs

- Use **"can"** for capability: "You can set the URL with `WAGTAIL_CLI_BASE_URL` or `--url`."
- Use **"should"** for recommendations: "Draft pages should be verified with `wt api pages get <ID> --version draft` before publishing."
- Reserve **"must"** for hard requirements, especially around destructive actions: "Mutating commands must be passed `--yes` when run non-interactively."
- Use **"may"** for possibility or optional behavior: "You may want to check `--dry-run` output before running a batch."

## Warnings, notes, and edge cases

We document limitations and open questions directly on the relevant page, not hidden in a separate caveats section.

- State limitations as facts, not apologies: "Image and document `update` cannot replace the file." "There is no anonymous mode."
- Call out **prototype** or **work in progress** status where it affects a decision — at the top of the README and the docs home, and in the [roadmap](../ROADMAP.md) — so readers see the status before investing in the content.
- When behavior differs or a command has a sharp edge, say so explicitly: "`update` and `delete` require `--yes` off a TTY, while actions such as `publish` run without a prompt."
- Keep the canonical version of user-facing behavior in one place — [`usage.md`](../usage.md) — and cross-link to it from contributor and agent docs rather than duplicating the details. Drift between the reference and the [agent skills](https://github.com/wagtail/wagtail-cli/tree/main/src/wagtail_cli/.agents/skills) is a common source of stale docs; when you change a command, update the reference first, then any skill that mentions it.

## Tooling

- Format and lint before committing with `just lint` and `just test`. Run `just format` to fix formatting issues automatically. See the [contribution guidelines](../CONTRIBUTING.md#quality-assurance) for the full list of scripts.
- Prettier formats JSON, YAML, and CSS; Ruff formats and lints Python. Markdown is currently **not** covered by either, so keep it tidy by hand and match the surrounding page.
- Build the docs before opening a pull request when you have touched `docs/`: `just docs-build` runs MkDocs in strict mode and fails on broken links, missing nav entries, and bad anchors. `just docs-serve` serves them locally at <http://localhost:8001>.
- Publishing behavior differs from GitHub rendering: admonitions and relative links resolve on the built site, while GitHub shows admonitions literally. Check both if a page is read in both places.
- The [agent skills](https://github.com/wagtail/wagtail-cli/tree/main/src/wagtail_cli/.agents/skills) are Markdown too, and are copied into the site at build time. They follow this guide, with one addition: keep the front matter `name`/`description` current, because those fields drive activation and are tested by the [eval suite](../evals/README.md).
