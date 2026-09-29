"""Promptfoo assertion: dry-run the model's `wt` commands and grade the requests.

The answer's bash block gets `--dry-run --json` injected into every `wt … api`
invocation and runs against a dummy site configuration, so a hallucinated flag
produces no request and the expected requests (`expect_requests`,
`forbid_methods`, `files` vars) are checked without a live Wagtail site.
Warning: this executes model-generated shell code; only run it against models
you trust.
"""

import importlib.util
import json
import os
import re
import subprocess
import tempfile

from pathlib import Path
from typing import Any


# The match rules live in a shared module so the Coder Eval grader asserts
# exactly the same thing; see its docstring. Loaded by path because Promptfoo
# loads this file itself (via `file://`), so a plain relative import would not
# resolve against a package.
_spec = importlib.util.spec_from_file_location(
    "_request_matching", Path(__file__).resolve().parent / "_request_matching.py"
)
_request_matching = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_request_matching)
describe_all = _request_matching.describe_all
match_expectations = _request_matching.match_expectations


CODE_BLOCK = re.compile(r"```(?:bash|sh|shell|console)?\s*\n(.*?)```", re.DOTALL)
# `wt` as a standalone token: not a path segment, not the tail of another word.
WT_TOKEN = re.compile(r"(?<![\w./-])wt(?=\s)")
PROMPT_PREFIX = re.compile(r"^\s*[$%>]\s+")
TIMEOUT_SECONDS = 60
DUMMY_BASE_URL = "https://wt-evals.invalid/api/v3/"
DUMMY_TOKEN = "wt-evals-dummy-token"  # noqa: S105 - placeholder, matches nothing


def _fail(reason: str) -> dict[str, Any]:
    return {"pass": False, "score": 0, "reason": reason}


def _extract_script(output: str) -> str | None:
    """Return the first fenced block that actually runs `wt`.

    Blocks that never invoke `wt` are ignored on purpose. Asked for terminal
    commands, a model that does not know the CLI sometimes answers with
    hand-written HTTP calls instead, which would otherwise neither exercise
    the CLI nor match any expected request.
    """
    for block in CODE_BLOCK.findall(output):
        lines = [PROMPT_PREFIX.sub("", line) for line in block.splitlines()]
        if any(WT_TOKEN.search(line) for line in lines):
            return "\n".join(lines)
    return None


def _merge_continuations(script: str) -> str:
    """Join backslash-continued lines so `wt` commands are single lines.

    The per-line extraction below needs the whole invocation — including any
    `$( … )` wrapper and pipeline — on one line. Heredoc bodies are not
    protected, but JSON never ends a line with a backslash in practice.
    """
    merged: list[str] = []
    pending = ""
    for line in script.splitlines():
        pending += line
        stripped = pending.rstrip()
        if stripped.endswith("\\") and (len(stripped) - len(stripped.rstrip("\\"))) % 2:
            pending = stripped[:-1] + " "
            continue
        merged.append(pending)
        pending = ""
    if pending:
        merged.append(pending)
    return "\n".join(merged)


def _split_pipelines(line: str) -> list[str]:
    """Return the `wt` invocations on a line, cut free of their pipelines.

    The skill tells agents to pipe `wt --json` output through `jq`, but a
    dry-run request fed into `jq` never reaches this grader's stdout parser.
    So each `wt …` invocation is extracted verbatim (quotes respected), any
    `VAR=$(wt …)` wrapper is dropped, and everything after a `|` is cut.
    Lines without a `wt` invocation — heredoc bodies, comments — pass
    through untouched so file-based recipes keep working.
    """
    extracted: list[str] = []
    index = 0
    length = len(line)
    while index < length:
        match = WT_TOKEN.search(line, index)
        if not match:
            break
        # Only a `wt` outside quotes counts; inside a string it is prose.
        prefix = line[: match.start()]
        if prefix.count('"') % 2 == 1 or prefix.count("'") % 2 == 1:
            index = match.end()
            continue
        start = match.start()
        cursor = match.end()
        end = length
        quote = ""
        # Depth of unclosed `(` from before the token, so the `)` that closes
        # a `VAR=$(wt …)` wrapper ends the invocation instead of joining it.
        depth = prefix.count("(") - prefix.count(")")
        while cursor < length:
            char = line[cursor]
            if quote:
                if char == quote:
                    quote = ""
            elif char in "'\"":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
                if depth == 0:
                    # This paren closes a `$( ` opened before the command.
                    end = cursor
                    break
            elif char in "|;&#":
                end = cursor
                break
            cursor += 1
        extracted.append(line[start:end].strip())
        index = cursor + 1
    if not extracted:
        return [line]
    if line.lstrip().startswith("#"):
        return [line]
    # Whatever followed the last cut — a `jq` pipeline, a comment — is noise
    # under dry-run, so only the extracted invocations are kept. A command
    # chained after `&&` on the same line is dropped too; multi-command
    # answers put each command on its own line.
    return extracted


def _instrument(command: str) -> str:
    """Turn one `wt` invocation into a JSON dry-run request printer.

    `--dry-run` alone prints the request in a human layout that the grader
    cannot parse line by line, so `--json` is forced as well: appended right
    before `api` so it wins, and swapped for a model's `--human` (the two
    cannot be combined). A model's own `--json` is left alone.
    """
    command = WT_TOKEN.sub("wt --dry-run", command, count=1)
    if "--human" in command:
        command = command.replace("--human", "--json")
    if "--json" not in command:
        index = 0
        length = len(command)
        while index < length:
            match = re.compile(r"(?<![\w-])api(?![\w-])").search(command, index)
            if not match:
                break
            before = command[: match.start()]
            if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
                command = f"{before}--json {command[match.start() :]}"
                break
            index = match.end()
    return command


def _add_dry_run(script: str) -> str:
    """Inject dry-run instrumentation into every `wt … api` invocation."""
    result = []
    for line in _merge_continuations(script).splitlines():
        if "--dry-run" in line:
            result.append(line)
            continue
        if "api" not in line or not WT_TOKEN.search(line):
            result.append(line)
            continue
        for part in _split_pipelines(line):
            if WT_TOKEN.search(part) and "api" in part:
                result.append(_instrument(part))
            else:
                result.append(part)
    return "\n".join(result)


def get_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    """Grade one model answer by dry-running the commands it contains."""
    script = _extract_script(output)
    if not script:
        return _fail("No bash block running `wt` in the answer.")

    variables = context.get("vars", {})
    script = _add_dry_run(script)

    with tempfile.TemporaryDirectory() as workdir:
        for name, content in (variables.get("files") or {}).items():
            path = os.path.join(workdir, name)
            os.makedirs(os.path.dirname(path) or workdir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)

        script_path = os.path.join(workdir, "commands.sh")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(script)

        # HOME points into the scratch directory so `wt api init` and
        # `~/.wagtail-cli.toml` cannot touch (or read) the real configuration;
        # the dummy variables override any site the environment names.
        env = {
            **os.environ,
            "HOME": workdir,
            "WAGTAIL_CLI_BASE_URL": DUMMY_BASE_URL,
            "WAGTAIL_CLI_TOKEN": DUMMY_TOKEN,
        }
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

    requests = []
    for line in run.stdout.splitlines():
        try:
            parsed = json.loads(line)
        except ValueError:
            continue
        if isinstance(parsed, dict) and "method" in parsed and "url" in parsed:
            requests.append(parsed)

    described = describe_all(requests)

    if not requests:
        detail = run.stderr.strip().splitlines()
        last_error = detail[-1] if detail else f"exit code {run.returncode}"
        return _fail(
            "No dry-run requests were produced — every `wt` command must have "
            f"failed. Last error: {last_error}"
        )

    ok, reason = match_expectations(
        variables.get("expect_requests", []),
        requests,
        variables.get("forbid_methods", []),
    )
    if not ok:
        return _fail(f"{reason} Observed:\n{described}")

    if run.returncode != 0:
        detail = run.stderr.strip().splitlines()
        reason += (
            f" (a command exited {run.returncode}: "
            f"{detail[-1] if detail else 'no stderr'})"
        )
    return {"pass": True, "score": 1, "reason": reason}
