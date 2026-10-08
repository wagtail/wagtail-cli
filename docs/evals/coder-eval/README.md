# Coder Eval task suite

A [Coder Eval](https://coder-eval.com/) suite covering the same tasks as the [Promptfoo skill evals](../README.md), run alongside them. It answers the same question — does loading the `wagtail` / `cli-api` / `cli-docs` skills change agent behaviour? — and adds the **trajectory**: turns, tokens, tool calls and duration per arm, which Promptfoo's answer-grading harness cannot report.

Promptfoo remains the primary harness; this suite runs alongside it. Neither replaces the other today (see [Trade-offs](#trade-offs)).

## Why run both

| Metric             | Promptfoo                         | Coder Eval                                                          |
| ------------------ | --------------------------------- | ------------------------------------------------------------------- |
| Overall time spent | Not reported                      | `duration` per task, aggregated per variant                         |
| Tokens needed      | Not reported                      | `token_usage` per task, aggregated per variant                      |
| Tool calls needed  | Only if the answer text is parsed | `commands_efficiency` + `CommandTelemetry`, counted from real calls |
| Skill activation   | Custom provider config            | `skill_triggered` criterion, first-class                            |
| Outcome grading    | Python grader over the answer     | `run_command` / file criteria over the sandbox                      |
| Statistics         | Single run                        | `repeats` + bootstrap CIs + paired mean-difference test             |

Promptfoo has to _infer_ what the agent did by re-parsing a markdown bash block from its reply. Coder Eval runs a real agent in a sandbox and records what it actually ran, so the efficiency metrics are first-class rather than inferred. The two suites agree on what "correct" means because they share their match rules (below).

## Tasks

One Coder Eval task per row of the Promptfoo suites.

| Coder Eval task               | Promptfoo row                                          | Suite    |
| ----------------------------- | ------------------------------------------------------ | -------- |
| `api_publish_blog_post`       | Publish a blog post with heading, paragraph and author | cli-api  |
| `api_update_draft`            | Update a draft without publishing it                   | cli-api  |
| `api_unpublish`               | Take a page offline without deleting it                | cli-api  |
| `api_list_posts`              | List blog posts under a section within the page cap    | cli-api  |
| `api_upload_image`            | Upload an image with a title                           | cli-api  |
| `docs_streamfield_validation` | Find and read the page on StreamField validation       | cli-docs |
| `docs_v3_create_operation`    | Pull up the v3 API operation that creates a page       | cli-docs |
| `docs_images_topic`           | Read the images topic                                  | cli-docs |

`wagtail_skill_triggers.yaml` is separate from the table above: a single dataset task whose 21 rows are the Wagtail ai-evals atomic task corpus prompts, copied verbatim (`ai-evals/tasks/atomic/<name>/instruction.md`). It measures trigger behaviour only — a stacked `skill_triggered` criterion reports a confusion matrix for the `wagtail` skill. Every development prompt is a positive; `hello-world` is the corpus control (negative); the `api-v3-recipe-editing` holdout is excluded. Its Promptfoo counterpart is `../../wagtail_trigger_skill.yaml`.

## Layout

```
docs/evals/coder-eval/
├── experiments/
│   ├── default.yaml            # single-arm runs (no -e)
│   └── wagtail_skills_ab.yaml  # the A/B: baseline vs with-skill
├── fixtures/
│   └── wt-site/                # copied into every sandbox
│       ├── bin/wt              # recording shim: logs argv, delegates, forces --dry-run
│       ├── .wagtail-cli.toml   # points wt at a dummy URL
│       ├── hero.png            # placeholder for the image-upload task
│       └── SITE.md             # site context the agent needs
└── tasks/
    ├── api_*.yaml              # one per cli-api row
    ├── docs_*.yaml             # one per cli-docs row
    └── graders/
        ├── check_api.py        # replays recorded argv, matches expect_requests
        └── check_docs.py       # replays recorded `wt docs`, checks expect_contains
```

## How the sandbox works

The trick that makes this tractable: **the real `wt --dry-run --json` already prints the HTTP request as JSON**, in the exact `{method, url, params, body, file}` shape the Promptfoo grader parses. So instead of building a fake API, we:

1. Ship `bin/wt` as a shim and have `sandbox.mock_path_dirs: ["bin"]` PATH-prepend it, so the agent's `wt` is ours.
2. The shim **records the argv** to `wt_calls.jsonl` at the sandbox root (the grader input) and **delegates** to the real `wt`, injecting `--dry-run --json` on `api` calls. The agent sees genuine CLI output; nothing touches the network.
3. `wt api whoami` is answered locally as a healthy connection, so the agent does not stall on auth.
4. `check_api.py` replays each recorded `wt api …` argv through the real CLI and matches the resulting request against the task's `expect_requests`. `check_docs.py` replays `wt docs …` and checks the output contains the task's `expect_contains`.

### Sharing the match rules

A task's `expect_requests` lives both in the Promptfoo YAML and in the Coder Eval task's `run_command` line (as the `EXPECT_REQUESTS` env var). Both harnesses import the same rules from [`../graders/_request_matching.py`](../graders/_request_matching.py), so they cannot drift. The difference between the harnesses is how the commands are obtained — a model's proposed answer versus a recorded trajectory — not what counts as correct.

If you change a task's expectations, change them in both files.

## Running

```sh
just eval-coder                  # full suite, both arms
just eval-coder --repeats 5      # raise the replicate count
just eval-coder-report           # the cross-variant report

# Validate without spending tokens:
cd docs/evals/coder-eval
coder-eval plan tasks/*.yaml -e experiments/wagtail_skills_ab.yaml
```

`just eval-init` installs the tooling (including the `litellm` extra the rubric judge needs). Before a real run, confirm the skill arm will actually load the skills:

```sh
opencode debug skill --pure   # lists every skill the CLI can load
```

The run log prints the resolved paths on the with-skill arm — one for the published `wagtail` skill, one for the `skill-data/` content skills:

```
opencode: injecting 2 skill path(s) via OPENCODE_CONFIG_CONTENT: ['…/.agents/skills', '…/skill-data']
```

`skill-data/` has no `skills/` subdir, so coder-eval treats it as a bare skills root (see `agents/_skills.py`). Only `wagtail` is auto-loadable in a real install; the harness loads `skill-data` to measure the content skills directly.

If that line is absent, the arm is silently measuring the bare model.

## Results

Full trajectory numbers for the latest recorded run live in [`../README.md`](../README.md#coder-eval). Each run writes its own report to `runs/<timestamp>/experiment.md` — generated locally and not committed (`runs/` is gitignored). `just eval-coder-report` renders it.

## Trade-offs

- **Two harnesses to maintain.** The tasks and their expectations are duplicated across Promptfoo and Coder Eval. The shared match module keeps them honest, but adding a task means editing two files.
- **The judge needs an extra.** Coder Eval's rubric judge routes to TensorX through its `litellm` transport, so it needs the `litellm` extra. Without it the judge fails loudly rather than scoring 0 silently.
- **No CI.** Neither harness runs in CI today. There is no scheduled job, no API key in the repository secrets, and cost is per-run. Recording a result means pasting it into the evals README by hand.
- **`wt api schema show` prints a Python repr, not JSON, under `--dry-run`.** The grader skips those lines (there is no request to match), but it means a recorded trajectory can contain entries that are not dry-run request documents. `check_api.py` filters to dicts for this reason.
- **OpenCode + Docker is unsupported** in Coder Eval (the CLI is not in its image and no credentials are passed through), so this runs under the default `tempdir` driver — a working directory, not a confinement boundary.
- **OpenCode ignores `allowed_tools` / `system_prompt`.** The CLI has no equivalent knob. The baseline arm therefore simply loads no skills, rather than being restricted to a tool subset.
- **No pricing rate for the TensorX models.** Token counts are exact and the provider's own per-call cost is booked, but the static rate card cannot price a partial/timed-out turn, so USD totals can understate the bill.
- **A judge call can occasionally return a verdict with no `score` field**, reported as `score field missing in judge verdict`. Treat it like the Promptfoo suite's empty-response row and re-run.
