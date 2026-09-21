# Skill evals

Promptfoo evals for the two agent skills in `src/wagtail_cli/.agents/skills/`, run through the OpenCode SDK provider on TensorX with `z-ai/glm-5.3-flash` as the default model under test.

Each suite (`wagtail_api_skill.yaml`, `wagtail_docs_skill.yaml`) runs every test against two arms that differ by exactly one tool:

| Arm | Tools | Question answered |
| --- | --- | --- |
| baseline | none | What can the model do from its own knowledge? |
| skill | `skill`, allowed to load only that suite's skill | Does loading the skill help? |

- Skill activation: rows restricted to the skill arm assert with `skill-used` that a fundamental task phrased the way a user would (no CLI named) actually loads the skill, and that an unrelated task does not.
- Task completion: both arms are asked for the exact terminal commands, and a grader runs them. `graders/run_api_commands.py` injects `--dry-run --json` into every `wt … api` invocation and runs the block against dummy credentials, then grades the exact requests (method, URL, params, body) — a hallucinated flag exits 2 and matches nothing, and no live Wagtail site is needed. `graders/run_docs_commands.py` runs `wt docs` commands as-is and checks the retrieved content.
- Gotchas with no command answer are graded by rubric, using a second model (`deepseek/deepseek-v4.1-flash`) from a different family so the suite is not grading itself.

Caveats: dry-run grading proves the CLI accepts the commands and builds the right request, not that a live site would accept the payload; the `--dry-run` rewrite drops `VAR=$(wt …)` capture, so prompts supply concrete inputs rather than values discovered from earlier commands.

## Requirements

- promptfoo 0.123.1 or newer (the `skill-used` assertion needs the session-history skill detection missing in 0.122) and `@opencode-ai/sdk` — `just eval-init` installs both.
- The OpenCode CLI, from https://opencode.ai/docs/.
- `wt` on PATH — the graders run the CLI the model names.
- `TENSORX_API_KEY` — the model under test and the rubric grader both run on TensorX.

## Running

```sh
just eval                                       # both suites
just eval docs/prompts/wagtail_api_skill.yaml   # one suite
just eval --repeat 3                            # agent runs are noisy; repeat before trusting a delta
just eval-view                                  # dashboard for the latest run
```

`WT_EVAL_MODEL` picks the model under test; it must be registered in `opencode.json` (default `z-ai/glm-5.3-flash`):

```sh
WT_EVAL_MODEL=qwen/qwen3.8-27b just eval
```

## Results snapshot

Single fresh runs, `--no-cache`, promptfoo 0.123.1. Agent runs are noisy — the create row below flipped between arms between sessions, so treat a one-run delta as indicative and confirm with `--repeat 3` before acting. "Activation" is the two skill-arm rows asserting the skill loads (or does not).

### wagtail-api (8 graded rows + 2 activation)

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash | 8/8 | 9/10 | 2/2 |
| qwen/qwen3.8-27b | 5/8 | 10/10 | 2/2 |

- glm's one skill-arm miss: the create row — it used generic block names (`heading`, `paragraph`) and `--field author_id:1` instead of the demo's `heading_block`/`paragraph_block` blocks and the required `blog_person_relationship` child relation from the skill's reference, even with the skill loaded.
- qwen's baseline misses: it twice answered without using `wt` at all (unpublish, list); its one empty response (StreamField rubric) was a provider error, not an answer.

### wagtail-docs (4 graded rows + 2 activation)

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash | 4/4 | 4/4 | 2/2 |
| qwen/qwen3.8-27b | 2/4 | 4/4 | 2/2 |

- qwen's baseline missed both lookups that need the reader: one empty response (provider error) and one rubric fail — it recommended parsing HTML with pandoc/trafilatura rather than `wt docs`.

Last updated: 2026-09-19.
