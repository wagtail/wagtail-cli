# Agent skills

Wagtail CLI includes [agent skills](https://agentskills.io/) that help agents get better results with agentic coding. They are published with the documentation site so they can be discovered and reused with a wide range of tools.

## Available skills

- [wagtail-api](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/wagtail-api/SKILL.md): Operate a Wagtail site via its API, with the Wagtail CLI.
- [wagtail-docs](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/wagtail-docs/SKILL.md): Read and search the Wagtail documentation from the terminal.

We make the skills available in multiple formats, for compatibility with a wide range of tools.

## In the installed package

Skills are bundled with the installed package and can be found under `wagtail_cli/.agents/skills/` in site-packages. You can manually create symlinks, or use the [Library Skills CLI](https://library-skills.io/) to manage them.

## Well Known Discovery

Machine-readable index of all skills: [`/agent-skills/index.json`](https://wagtail.github.io/wagtail-cli/.well-known/agent-skills/index.json). This is per the [Well Known Discovery RFC](https://github.com/cloudflare/agent-skills-discovery-rfc). Agents that support the format can fetch it to discover the skills.

## AI catalog

Machine-readable index that also covers options other than skills: [`ai-catalog.json`](https://wagtail.github.io/wagtail-cli/.well-known/ai-catalog.json). This is per the [AI Catalog](https://ai-catalog.io/) specification.

## Evaluating the skills

We run [skills evaluations](prompts/README.md) to improve how the skills work across a wide range of models. Consider whether the skills will be relevant for your usage depending on results observed with those tested models.
