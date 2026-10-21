# Agent skills

Wagtail CLI includes [agent skills](https://agentskills.io/) that help agents get better results with agentic coding. They are published with the documentation site so they can be discovered and reused with a wide range of tools.

## Available skills

- [wagtail](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/wagtail/SKILL.md): triggers on any Wagtail task and routes the agent to the detailed workflow for the task at hand.

We provide only one evergreen skill out of the box. On usage, it will load our official [agent skills for developers](https://wagtail.org/ai/agent-skills-for-developers/) on demand.

## Install the skills

We make the skill available in multiple formats, for compatibility with a wide range of tools. To install directly as a skill, for multiple agents / harnesses:

```bash
# Directly with the CLI, global:
mkdir -p ~/.agents/skills/wagtail && wt skills get wagtail > ~/.agents/skills/wagtail/SKILL.md
# Directly with the CLI, local:
mkdir -p .agents/skills/wagtail && wt skills get wagtail > .agents/skills/wagtail/SKILL.md
```

### As a plugin

It’s also available as a plugin, follow [Agent Plugins compatible clients](https://agent-plugins.org/compatible-clients) installation instructions, using this repository as the plugin source: `wagtail/wagtail-cli`. Here is an example with `copilot`:

```bash
copilot plugin marketplace add wagtail/wagtail-cli
copilot plugin install wagtail-cli@wagtail-cli
# Should say:
# Plugin "wagtail-cli" installed successfully. Installed 1 skill.
```

## Loading skills from the CLI

Agents that have the CLI installed load skill content from it directly, so the instructions always match the installed version rather than a snapshot downloaded earlier. The `wagtail` stub exists to tell agents to do this:

```bash
wt skills list                 # skills available on the installed version
wt skills get cli-api          # or the short alias `docs` for cli-docs
wt skills get cli-api --full   # include references/ and templates/
wt skills get cli-docs         # read and search the documentation
wt skills path cli-api         # where the skill's files live on disk
```

`wt skills get` prints the skill's `SKILL.md`; `--full` appends its reference files, which is how the cli-api skill exposes its full command and content-writing references. `wt skills list` and `--all` skip the `wagtail` stub itself: it is the entry point, not one of the skills to load. Add `--json` for machine-readable output.

## In the installed package

The `wagtail` skill is bundled under `wagtail_cli/.agents/skills/` in site-packages, and the CLI-served content under `wagtail_cli/skill-data/`. You can manually create symlinks, use the [Library Skills CLI](https://library-skills.io/) to manage the `wagtail` skill, or have agents load any of them with [`wt skills`](#loading-skills-from-the-cli).

## Well Known Discovery

Machine-readable index of the published skills: [`/agent-skills/index.json`](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/index.json). This is per the [Well Known Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc). Agents that support the format can fetch it to discover the skills.

## AI catalog

Machine-readable index that also covers options other than skills: [`ai-catalog.json`](https://wagtail.github.io/wagtail-cli/.well-known/ai-catalog.json). This is per the [AI Catalog](https://ai-catalog.io/) specification.

## Evaluating the skills

We run [skills evaluations](evals/README.md) to improve how the skills work across a wide range of models. Consider whether the skills will be relevant for your usage depending on results observed with those tested models.
