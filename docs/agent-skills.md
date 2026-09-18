# Agent skills

wagtail-cli ships two [agent skills](https://agentskills.io/) that help agents get better results with agentic coding. They are published with the documentation site so they can be discovered and reused with a wide range of tools.

| Skill | Purpose |
|---|---|
| `wagtail-api` | Operate a Wagtail site through `wt api`: content model discovery, pages, media, snippets, sites, locales, redirects, with the gotchas agents hit most and a `references/` directory for the full command surface and content payloads. |
| `wagtail-docs` | Read and search docs.wagtail.org and the v3 API reference with `wt docs`, in a few lines, so agents stop fetching HTML pages. |

## Editing the skills

Skills live under `src/wagtail_cli/.agents/skills/`, one directory per skill. `SKILL.md` is the entry point agents load; longer material lives in `references/` and is linked from `SKILL.md` with relative paths so agents only read it when needed. The post-build hook in `docs/hooks.py` publishes each skill directory automatically, minus the `evals/` directory used to test the skill.

## In the installed package

The same skill directories ship inside the package: after `uv tool install wagtail-cli` or `pip install wagtail-cli`, find them under `wagtail_cli/.agents/skills/` in site-packages (`python -c "import wagtail_cli, pathlib; print(pathlib.Path(wagtail_cli.__file__).parent / '.agents/skills')"`).

## Direct links to the skills

Each skill is served from the documentation site at `.well-known/agent-skills/<name>/SKILL.md`, for example `.well-known/agent-skills/wagtail-api/SKILL.md`, with any reference files next to it under `references/`. Open the URL to read a skill, point an agent at it, or download the directory and place it at `.agents/skills/<name>/` in your project so tooling that reads local skills picks it up.

## Well Known Discovery

Machine-readable index of all skills: `/.well-known/agent-skills/index.json`. This is per the [Well Known Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc). Agents that support the format can fetch it to discover the skills.

## AI catalog

Machine-readable index that also covers options other than skills: `/.well-known/ai-catalog.json`. This is per the [AI Catalog](https://ai-catalog.io/) specification.

## How it works

During the documentation build, `mkdocs-simple-hooks` runs `docs/hooks.py:on_post_build`, which copies each skill and generates both discovery catalogs. Set `include-hidden-files: true` on the Pages upload in `.github/workflows/test.yml` so the `.well-known/` directory is included in the deployed artifact.
