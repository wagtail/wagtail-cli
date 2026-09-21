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

Caveats: dry-run grading proves the CLI accepts the commands and builds the right request, not that a live site would accept the payload; the `--dry-run` rewrite drops `VAR=$(wt …)` capture, so prompts supply concrete inputs rather than values discovered from earlier commands. The `read`, `grep`, `glob` and `list` tools are disabled explicitly on both arms: the promptfoo opencode:sdk provider turns them on by default whenever `working_dir` is set, even with `'*': false`, which let the baseline read the repo (including the eval configs, the skills and this README) and answer from there instead of from its own knowledge. Disabling them means the skill tool loads `SKILL.md` only — `references/` files linked from it are unreachable, so `SKILL.md` needs to stand alone. The repo's `AGENTS.md` is still injected into the context of both arms by OpenCode; it describes the project but not the CLI, so it does not teach the baseline any commands.

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

Post-leak-fix numbers (see caveats): `--no-cache --repeat 3`, promptfoo 0.123.1, one model per suite, arms with all filesystem tools disabled. The pre-fix snapshot (2026-09-19) measured all three models with the baseline able to read the repo, so those numbers are not comparable and were dropped; rerun the other models with `WT_EVAL_MODEL` to repopulate the table. "Activation" is the two skill-arm rows asserting the skill loads (or does not).

### wagtail-api (8 graded rows + 2 activation), z-ai/glm-5.3-flash, eval-ChC-2026-09-21T15:06:49

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash | 3/24 | 20/30 | 6/6 |

- The one baseline pass is the StreamField replace-whole rubric, answered correctly from generic Wagtail knowledge; every command row now fails honestly — the model suggests `git clone` of the Wagtail repo or generic curl against the API instead of `wt`.
- The three skill-arm misses are the create, update-draft and image-upload rows, 0/3 each: with `references/` unreachable (read tools disabled) the model gets the command surface wrong from `SKILL.md` alone — `--field key=value` instead of `KEY:VALUE`, `--file` instead of the positional file argument, and generic block/relation shapes instead of the demo's. The skill needs to stand alone or the eval needs a fixture working_dir; the pre-fix runs did not show these misses because the model could read `references/` from the repo.

### wagtail-docs (4 graded rows + 2 activation), z-ai/glm-5.3-flash, eval-Y0n-2026-09-21T15:06:49

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash | 0/12 | 18/18 | 6/6 |

- Clean sweep for the skill arm across all three repeats, and the baseline now fails every row from pure memory (clone-the-repo and curl advice, invented docs paths) — the intended contrast.

Last updated: 2026-09-21.
