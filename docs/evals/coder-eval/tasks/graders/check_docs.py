#!/usr/bin/env python3
"""Grade the recorded `wt docs` calls against a task's expected content.

Runs as a Coder Eval `run_command` criterion from the sandbox root. Reads the
``wt_calls.jsonl`` written by the ``bin/wt`` shim, replays each recorded
``wt docs …`` argv for real (the docs reader needs no site configuration), and
checks the combined output contains every fragment named in the
``EXPECT_CONTAINS`` env var — the same assertion the Promptfoo docs grader
(``../../graders/run_docs_commands.py``) makes against a model's proposed answer.

Replaying rather than trusting the byte-for-byte `expect_contains` on the
recorded stdout means the check is "the agent's commands, run now, retrieve the
material" — identical in spirit to the Promptfoo grader.

Exit 0 = the expected content was retrieved; non-zero = it was not.
"""

from __future__ import annotations

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
TIMEOUT_SECONDS = 60


def _iter_docs_calls():
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
        if "docs" in argv:
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


def _run(argv: list[str], real: str) -> str:
    env = dict(os.environ)
    completed = subprocess.run(  # noqa: S603 - the eval replays model output on purpose
        [real, *argv[1:]],
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return f"{completed.stdout}\n{completed.stderr}"


def main() -> int:
    shim_dir = LOG.parent / "bin"
    real = _resolve_real_wt(shim_dir)
    if real is None:
        print("the real `wt` CLI is not on PATH", file=sys.stderr)
        return 2

    expected = json.loads(os.environ.get("EXPECT_CONTAINS", "[]"))

    calls = list(_iter_docs_calls())
    if not calls:
        print(
            "no `wt docs` invocation was recorded — the agent did not use the docs reader",
            file=sys.stderr,
        )
        return 1

    combined = "\n".join(_run(argv, real) for argv in calls)
    missing = [fragment for fragment in expected if fragment not in combined]
    if missing:
        print(f"output is missing {missing!r}", file=sys.stderr)
        print(f"output tail: {combined.strip()[-400:]}", file=sys.stderr)
        return 1

    print(f"OK: retrieved all {len(expected)} expected fragment(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
