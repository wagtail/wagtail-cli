"""Promptfoo assertion: run the model's `wt docs` commands and grade the output.

`wt docs` needs no configuration, so the extracted bash block runs as-is and
must produce the expected content (`expect_contains` var).
Warning: this executes model-generated shell code; only run it against models
you trust.
"""

import os
import re
import subprocess
import tempfile

from typing import Any


CODE_BLOCK = re.compile(r"```(?:bash|sh|shell|console)?\s*\n(.*?)```", re.DOTALL)
WT_DOCS = re.compile(r"(?<![\w./-])wt\s+docs\b")
PROMPT_PREFIX = re.compile(r"^\s*[$%>]\s+")
TIMEOUT_SECONDS = 60


def _fail(reason: str) -> dict[str, Any]:
    return {"pass": False, "score": 0, "reason": reason}


def _extract_script(output: str) -> str | None:
    """Return the first fenced block that actually runs `wt docs`.

    Blocks without a `wt docs` invocation are ignored on purpose: asked how
    to look something up in the Wagtail docs, a model without the skill
    answers with `curl` or WebFetch, which is precisely the behaviour the
    skill exists to replace.
    """
    for block in CODE_BLOCK.findall(output):
        lines = [PROMPT_PREFIX.sub("", line) for line in block.splitlines()]
        if any(WT_DOCS.search(line) for line in lines):
            return "\n".join(lines)
    return None


def get_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    """Grade one model answer by running the docs commands it contains."""
    script = _extract_script(output)
    if not script:
        return _fail("No bash block running `wt docs` in the answer.")

    with tempfile.TemporaryDirectory() as workdir:
        script_path = os.path.join(workdir, "commands.sh")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(script)

        # HOME points into the scratch directory so the run cannot read the
        # real `~/.wagtail-cli.toml` even though `wt docs` ignores it anyway.
        env = {**os.environ, "HOME": workdir}
        try:
            run = subprocess.run(  # noqa: S603 - the eval runs model output on purpose
                ["/bin/bash", script_path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=workdir,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return _fail(f"Commands did not finish within {TIMEOUT_SECONDS}s.")

    combined = f"{run.stdout}\n{run.stderr}"

    missing = [
        fragment
        for fragment in context.get("vars", {}).get("expect_contains", [])
        if fragment not in combined
    ]
    if missing:
        tail = combined.strip()[-400:]
        return _fail(f"Output is missing {missing!r}. Output tail: {tail}")

    return {
        "pass": True,
        "score": 1,
        "reason": "Commands ran and retrieved the material.",
    }
