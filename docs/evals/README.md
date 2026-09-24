# Skill evals

Evaluation suites for the agent skills that are [bundled with the CLI](../agent-skills.md). Running with Promptfoo, with models taken from [Wagtail agentic engineering recommendations](https://wagtail.org/ai/agentic-engineering-recommendations/).

For each skill, we run two suites: a baseline with nothing loaded, and one with our skills. We test:

- Skill activation: whether the skill activates when mentioning potential related tasks, without necessarily directly prompting for "use Wagtail CLI".
- Task completion: whether the CLI commands provided by the agent actually exist, and work as explained, and help in completing the task.
- Gotchas with no command answer. Graded by rubric, using a separate model family.

## Requirements

- Promptfoo with the OpenCode AI SDK (`just eval-init`)
- [OpenCode CLI](https://opencode.ai/docs/)
- `wt` on PATH. The graders run the CLI from there.
- `TENSORX_API_KEY` — the model under test and the rubric grader both run on TensorX.

## Running

```sh
just eval                                       # both suites
just eval docs/evals/wagtail_api_skill.yaml   # one suite
just eval --repeat 3                            # agent runs are noisy; repeat before trusting a delta
just eval-view                                  # dashboard for the latest run
```

`EVAL_MODEL` picks the model under test; it must be registered in `opencode.json` (default `z-ai/glm-5.3-flash`):

```sh
EVAL_MODEL=qwen/qwen3.8-27b just eval
```

## Results snapshot

Post-leak-fix numbers (see caveats): `--no-cache`, promptfoo 0.123.1, baseline with all filesystem tools disabled, skill arm with `read` scoped to the skills directory. Single runs — confirm deltas with `--repeat 3` before acting. The pre-fix snapshot (2026-09-19) measured all three models with the baseline able to read the repo, so those numbers are not comparable and were dropped. "Activation" is the two skill-arm rows asserting the skill loads (or does not).

### wagtail-api (8 graded rows + 2 activation)

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash (eval-fIc-2026-09-21T16:09:08) | 1/8 | 8/10 | 2/2 |
| qwen/qwen3.8-27b (eval-RNf-2026-09-21T16:14:24) | 1/8 | 8/10 | 2/2 |
| qwen/qwen3.5-9b (eval-FZi-2026-09-21T16:32:38) | 1/8 | 5/10 | 2/2 |

- Every baseline passes exactly one row: the StreamField replace-whole rubric, answered from generic Wagtail knowledge. Every command row now fails honestly — the models suggest `git clone` of the Wagtail repo or generic curl against the API instead of `wt`.
- Every skill arm misses the create row: the models follow the skill's schema-check strategy but still build partly generic payloads (`size: h2` on the heading, no `blog_person_relationship`) instead of the demo's shapes — the persistent hard row across configs and models.
- glm's other miss (list) is new this run and passed in earlier runs of the same config (eval-6go-2026-09-21T15:51:39, 9/10) — noise; treat one-run deltas as indicative. The intermediate all-read-disabled config (eval-ChC-2026-09-21T15:06:49) also failed update-draft and image-upload because the command syntax in `references/commands.md` was unreachable; the scoped read restores those.
- qwen3.8-27b's other miss (unpublish) was an empty response — provider error, not an answer (its baseline hit one on the same row). qwen3.5-9b is the local-model test case: activation works, but without reliable command syntax it fails five rows (`--dry-run` rewrites, schema checks and `references/` lookups notwithstanding).

### wagtail-docs (4 graded rows + 2 activation), z-ai/glm-5.3-flash, eval-Y0n-2026-09-21T15:06:49

| Model | baseline | skill | activation |
| --- | --- | --- | --- |
| z-ai/glm-5.3-flash | 0/4 | 4/4 | 2/2 |

- Baseline fails every row from pure memory (clone-the-repo and curl advice, invented docs paths); the skill arm passes everything — the intended contrast. Numbers are from the intermediate all-read-disabled config; the scoped read only adds access the skill arm already used.

Last updated: 2026-09-21.
