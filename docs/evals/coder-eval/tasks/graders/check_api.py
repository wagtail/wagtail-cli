#!/usr/bin/env python3
"""Grade the recorded `wt` calls against a task's expected requests.

Runs as a Coder Eval `run_command` criterion from the sandbox root. Reads the
``wt_calls.jsonl`` written by the ``bin/wt`` shim, replays each recorded
``wt api …`` argv through the real CLI with ``--dry-run --json`` to recover the
HTTP request it would have sent, then asserts the task's `expect_requests` /
`forbid_methods` against those requests.

The match rules are imported from the shared ``_request_matching`` module so a
task's expectations mean exactly what they mean in the Promptfoo suite — the
difference between the harnesses is how the commands are obtained (a model's
proposed answer vs. a recorded trajectory), not what counts as correct.

The expectations arrive as JSON in the ``EXPECT_REQUESTS`` and
``FORBID_METHODS`` env vars, set from the task's ``run_command`` line. Exit 0 =
the expected requests were made; non-zero = they were not.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from pathlib import Path


HERE = Path(__file__).resolve().parent
# `run_command` executes with the sandbox as its working directory, and the shim
# writes the log at the sandbox root — NOT under $TASK_DIR, which is the task's
# own directory on the host.
LOG = Path.cwd() / "wt_calls.jsonl"

DUMMY_BASE_URL = "https://wt-evals.invalid/api/v3/"
DUMMY_TOKEN = "wt-evals-dummy-token"  # noqa: S105 - placeholder


def _load_matching():
    """Load the shared match rules from the Promptfoo graders directory.

    Loaded by path rather than imported as a package: this file is invoked as a
    standalone script inside a sandbox that has no Python package layout.
    """
    # docs/evals/coder-eval/tasks/graders -> docs/evals/graders
    shared = HERE.parent.parent.parent / "graders" / "_request_matching.py"
    spec = importlib.util.spec_from_file_location("_request_matching", shared)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _iter_api_calls():
    if not LOG.exists():
        return
    for line in LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        argv = record.get("argv") or []
        if "api" in argv:
            yield argv


def _resolve_real_wt(shim_dir: Path) -> str | None:
    """The real `wt`, skipping the shim's directory on PATH."""
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory or Path(directory).resolve() == shim_dir.resolve():
            continue
        candidate = Path(directory) / "wt"
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _request_for(argv: list[str], real: str) -> dict | None:
    env = dict(os.environ)
    env["WAGTAIL_CLI_BASE_URL"] = DUMMY_BASE_URL
    env["WAGTAIL_CLI_TOKEN"] = DUMMY_TOKEN
    if "--dry-run" not in argv:
        argv = [argv[0], "--json", "--dry-run", *argv[1:]]
    completed = subprocess.run(  # noqa: S603 - the eval replays model output on purpose
        [real, *argv[1:]],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    text = completed.stdout.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Some subcommands (e.g. `schema show`) print a Python repr rather than
        # JSON even under --dry-run. Those carry no request to match.
        return None
    # Guard against a source that decodes to a scalar/string rather than an object.
    return parsed if isinstance(parsed, dict) else None


def main() -> int:
    matching = _load_matching()
    shim_dir = LOG.parent / "bin"
    real = _resolve_real_wt(shim_dir)
    if real is None:
        print("the real `wt` CLI is not on PATH", file=sys.stderr)
        return 2

    expectations = json.loads(os.environ.get("EXPECT_REQUESTS", "[]"))
    forbid = json.loads(os.environ.get("FORBID_METHODS", "[]"))

    requests = [
        request
        for request in (_request_for(argv, real) for argv in _iter_api_calls())
        if request
    ]
    if not requests:
        print(
            "no `wt api` invocation produced a request document — "
            "the agent did not use the CLI",
            file=sys.stderr,
        )
        return 1

    ok, reason = matching.match_expectations(expectations, requests, forbid)
    if ok:
        print(f"OK: {reason}")
        return 0

    print(f"FAIL: {reason}", file=sys.stderr)
    print("Observed:", file=sys.stderr)
    print(matching.describe_all(requests), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
