# Agent skills

Wagtail CLI includes [agent skills](https://agentskills.io/) that help agents get better results with agentic coding. They are published with the documentation site so they can be discovered and reused with a wide range of tools.

## Available skills

- [wagtail](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/wagtail/SKILL.md): triggers on any Wagtail task and routes the agent to the detailed workflow for the task at hand.

`wagtail` is the only skill published here, and the only one that lives in the
package's `.agents/skills/` directory, so agent tooling can install and load it.
The detailed content it loads is bundled for the CLI to serve on demand under
`skill-data/` and is never auto-loaded. `wt skills list` lists them: `core`
(orientation for work on Wagtail projects), `cli-api` (operate a site via the
v3 API), `cli-docs` (read and search the documentation), and the specialized
project skills `api`, `backend`, `content-modeling`, `frontend`, and
`upgrade-wagtail`.

We make the skill available in multiple formats, for compatibility with a wide range of tools.

## Loading skills from the CLI

Agents that have the CLI installed load skill content from it directly, so the
instructions always match the installed version rather than a snapshot
downloaded earlier. The `wagtail` stub exists to tell agents to do this:

```bash
wt skills list                 # skills available on the installed version
wt skills get cli-api          # or the short alias `docs` for cli-docs
wt skills get cli-api --full   # include references/ and templates/
wt skills get cli-docs         # read and search the documentation
wt skills path cli-api         # where the skill's files live on disk
```

`wt skills get` prints the skill's `SKILL.md`; `--full` appends its reference
files, which is how the cli-api skill exposes its full command and
content-writing references. `wt skills list` and `--all` skip the `wagtail`
stub itself: it is the entry point, not one of the skills to load. Add `--json`
for machine-readable output.

## In the installed package

The `wagtail` skill is bundled under `wagtail_cli/.agents/skills/` in
site-packages, and the CLI-served content under `wagtail_cli/skill-data/`. You
can manually create symlinks, use the [Library Skills CLI](https://library-skills.io/)
to manage the `wagtail` skill, or have agents load any of them with
[`wt skills`](#loading-skills-from-the-cli).

## Well Known Discovery

Machine-readable index of the published skills: [`/agent-skills/index.json`](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/index.json). This is per the [Well Known Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc). Agents that support the format can fetch it to discover the skills.

## AI catalog

Machine-readable index that also covers options other than skills: [`ai-catalog.json`](https://wagtail.github.io/wagtail-cli/.well-known/ai-catalog.json). This is per the [AI Catalog](https://ai-catalog.io/) specification.

## Evaluating the skills

We run [skills evaluations](evals/README.md) to improve how the skills work across a wide range of models. Consider whether the skills will be relevant for your usage depending on results observed with those tested models.
