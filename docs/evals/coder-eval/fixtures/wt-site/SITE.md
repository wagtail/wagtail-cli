# Site context the fixture ships, so the agent does not have to hunt for it.

# Kept short and factual — the skill is what should supply command syntax.

## Wagtail demo site

- API base URL: `https://wt-evals.invalid/api/v3/`
- Auth: configured through `.wagtail-cli.toml` in this directory.
- Blog index: page id `4`, path `/blog/`.
- Blog page type: `blog.BlogPage` (body is a StreamField).
- Author ids: `1` (and `2`).
