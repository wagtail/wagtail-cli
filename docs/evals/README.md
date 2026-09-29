# Skill evals

Evaluation suites for the agent skills that are [bundled with the CLI](../agent-skills.md). Models come from the [Wagtail agentic engineering recommendations](https://wagtail.org/ai/agentic-engineering-recommendations/).

For each skill, we run two suites: a baseline with nothing loaded, and one with our skills. We test:

- Skill activation: whether the skill activates when mentioning potential related tasks, without necessarily directly prompting for "use Wagtail CLI".
- Task completion: whether the CLI commands provided by the agent actually exist, and work as explained, and help in completing the task.
- Gotchas with no command answer. Graded by rubric, using a separate model family.

## Harnesses

We run these suites with two tools, on the same tasks and the same model, so the
results can be compared and either number trusted:

| | what it grades | what it is good for |
| --- | --- | --- |
| [Promptfoo](https://promptfoo.dev/) | the agent's written **answer** | command correctness and rubric grading |
| [Coder Eval](coder-eval/README.md) | the agent's **trajectory** in a sandbox | time, tokens and tool calls per arm |

Promptfoo is the primary harness. Coder Eval runs alongside it to add the
efficiency metrics Promptfoo cannot report, and to check the two agree on what
"correct" means. Neither replaces the other today; see
[coder-eval/README.md](coder-eval/README.md) for the trade-offs.

## Requirements

- [OpenCode CLI](https://opencode.ai/docs/)
- `wt` on PATH. The graders run the CLI from there.
- `TENSORX_API_KEY` — the model under test and the rubric grader both run on TensorX.
- `just eval-init` installs the harness tooling (Promptfoo and Coder Eval).

## Running

```sh
just eval                                       # Promptfoo: both suites
just eval docs/evals/wagtail_api_skill.yaml     # Promptfoo: one suite
just eval --repeat 3                            # agent runs are noisy; repeat before trusting a delta
just eval-view                                  # Promptfoo dashboard for the latest run

just eval-coder                                 # Coder Eval: the same tasks, both arms
just eval-coder --repeats 5                     # raise the replicate count
just eval-coder-report                          # Coder Eval report for the latest run
```

`EVAL_MODEL` picks the Promptfoo model under test; it must be registered in `opencode.json` (default `z-ai/glm-5.3-flash`):

```sh
EVAL_MODEL=qwen/qwen3.8-27b just eval
```

The Coder Eval model under test is set in `coder-eval/experiments/wagtail_skills_ab.yaml`, and its rubric judge in each `docs_*.yaml` task's `checker_context`.

## Known friction

Things a future maintainer will run into, and what to do about them:

- **The two harnesses share their match rules, by design.** A task's
  `expect_requests` lives in the Promptfoo YAML and in the Coder Eval task's
  `run_command` line; both import
  [`graders/_request_matching.py`](graders/_request_matching.py) so they cannot
  drift. If you change a task's expectation, change it in both places.
- **Coder Eval's rubric judge needs the `litellm` extra.** `just eval-init`
  installs it (`uv tool install coder-eval --with litellm`). Without it the
  judge fails loudly rather than scoring 0 silently.
- **Coder Eval's with-skill arm needs `$SKILLS_PATH`.** `just eval-coder` exports
  it and fails fast if it is unset; if you invoke `coder-eval` directly, export
  it yourself or the arm silently measures the bare model.
- **`wt docs` has no `--outline` flag.** The `wagtail-docs` skill's SKILL.md
  suggests one that the CLI does not implement. Agents that follow the example
  produce a failed command; a `command_executed` criterion with
  `require_success: true` catches that, but the skill text should be fixed.
- **OpenCode + Docker is unsupported in Coder Eval** (the CLI is not in its
  image), so the sandbox is a tempdir — a working directory, not a confinement
  boundary. OpenCode also ignores `allowed_tools`/`system_prompt`; the baseline
  arm simply loads no skills rather than restricting tools.
- **Both harnesses are local-only.** Neither runs in CI; there is no scheduled
  job and no API key configured there. Committing a run means recording it by
  hand in this file.
- **`wt api schema show` prints a Python repr, not JSON, under `--dry-run`.**
  The Coder Eval grader skips such lines. Keep it in mind if a recorded
  trajectory ever looks like it is missing a command.

## Results snapshot

Promptfoo numbers, post-leak-fix (see caveats): `--no-cache`, promptfoo 0.123.1, baseline with all filesystem tools disabled, skill arm with `read` scoped to the skills directory. Single runs — confirm deltas with `--repeat 3` before acting. The pre-fix snapshot (2026-09-19) measured all three models with the baseline able to read the repo, so those numbers are not comparable and were dropped. "Activation" is the two skill-arm rows asserting the skill loads (or does not).

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

### Coder Eval

`tensorx/deepseek/deepseek-v4.1-flash`, 5 replicates per (task, arm), 8 tasks × 2
arms, graded by `qwen/qwen3.8-flash-next` (a different family from the model
under test). Run `2026-09-29_17-00-11`. Bold marks the better arm.

| Metric | baseline | with-skill |
| --- | --- | --- |
| Mean score | 0.548 ± 0.172 | **0.925 ± 0.074** |
| Tasks won | 0/8 | **8/8** |
| Task pass rate | 0% | 37.5% |
| Tool calls per run | 13.0 | **8.4** |
| Assistant turns per run | 10.2 | **8.2** |
| Tokens per run | 218,188 | **166,784** |
| Duration per run | 72.5s | **54.2s** |

Paired mean difference (baseline − with-skill): **−0.378** (95% CI −0.505 to
−0.251, Cohen's d = −2.49, p < 0.001). The skill arm wins every task, uses
~24% fewer tokens, ~35% fewer tool calls, and ~25% less wall-clock time.

Per-task scores (baseline → with-skill):

| Task | baseline | with-skill |
| --- | --- | --- |
| `unpublish_not_delete` | 0.667 | 1.000 |
| `list_blog_posts` | 0.600 | 1.000 |
| `docs_images_topic` | 0.417 | 0.984 |
| `publish_blog_post` | 0.200 | 0.800 |
| `update_draft_no_publish` | 0.600 | 0.867 |
| `docs_v3_create_operation` | 0.730 | 0.946 |
| `docs_streamfield_validation` | 0.502 | 0.940 |
| `upload_image` | 0.667 | 0.867 |

Notes:

- The skill arm still misses `publish_blog_post` on 2/5 replicates and
  `update_draft_no_publish` / `upload_image` on 1/5 each — the same
  partial-payload failures the Promptfoo suite documents for its create row,
  which is a useful cross-harness agreement.
- Almost every run overshoots its `commands_efficiency` budget. That criterion
  is `weight: 0` (informational), so it does not gate, but it shows both arms
  loop more than the skill's intended `whoami → schema → create` path.
- Two with-skill rows scored on a judge hiccup: one got no verdict
  (`Judge did not call submit_verdict`), one a low score with a reasoning
  rationale. Treat single judge rows as noisy; the paired aggregate is the
  signal.
- Baseline never passes a task (0/40 replicates); its 0.548 mean comes from
  partial credit on the non-gating criteria.

Last updated: 2026-09-29.
