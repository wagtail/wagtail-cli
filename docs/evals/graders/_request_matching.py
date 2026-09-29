"""Shared request-matching logic for the skill eval graders.

Both eval harnesses grade the same thing — the HTTP request a `wt … api` command
would send — but get there differently:

- Promptfoo receives a model *answer* and extracts + dry-runs the bash block the
  model wrote (`run_api_commands.py`).
- Coder Eval receives the *argv the agent actually ran* from a recorder shim and
  replays each through the CLI (`../coder-eval/tasks/graders/check_api.py`).

Keeping the match rules here means a task's `expect_requests` is asserted
identically in both, so the two suites cannot drift apart on what "correct"
means. Only the extraction differs, and that difference is the point: one
harness reads a proposed answer, the other reads a real trajectory.
"""

from __future__ import annotations

import json

from typing import Any


def subset(expected: Any, observed: Any) -> bool:
    """Recursive subset match; lists match positionally.

    Supports two operators inside ``expected`` mappings:

    - ``{"$lte": number}`` — ``observed`` must compare ``<=``.
    - ``{"$exists": true}`` — ``observed`` merely needs the key present, which
      the parent key check already guarantees.
    """
    if isinstance(expected, dict):
        if "$lte" in expected:
            try:
                return float(observed) <= float(expected["$lte"])
            except (TypeError, ValueError):
                return False
        if "$exists" in expected:
            return True
        if not isinstance(observed, dict):
            return False
        return all(
            key in observed and subset(value, observed[key])
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        return (
            isinstance(observed, list)
            and len(expected) <= len(observed)
            and all(
                subset(item, value)
                for item, value in zip(expected, observed, strict=False)
            )
        )
    if expected == "$list":
        return isinstance(observed, list)
    return expected == observed


def request_matches(expected: dict[str, Any], observed: dict[str, Any]) -> bool:
    """Does one observed dry-run request satisfy one expected request?

    Recognised keys: ``method``, ``url_suffix``, ``params``, ``body``, and
    ``file_required`` (an upload must carry a file).
    """
    if "method" in expected and expected["method"] != observed.get("method"):
        return False
    if "url_suffix" in expected and not str(observed.get("url", "")).endswith(
        expected["url_suffix"]
    ):
        return False
    if "params" in expected and not subset(expected["params"], observed.get("params")):
        return False
    if "body" in expected and not subset(expected["body"], observed.get("body")):
        return False
    if expected.get("file_required") and not observed.get("file"):
        return False
    return True


def match_expectations(
    expectations: list[dict[str, Any]],
    requests: list[dict[str, Any]],
    forbidden_methods: list[str] | None = None,
) -> tuple[bool, str]:
    """Match ``expectations`` against ``requests`` in order.

    Returns ``(ok, reason)``. A forbidden method present anywhere is a failure
    before any expectation is checked. Expectations are matched in order so a
    task cannot pass by making the right call in the wrong sequence.
    """
    requests = [request for request in requests if isinstance(request, dict)]
    forbidden = [
        method
        for method in forbidden_methods or []
        if any(request.get("method") == method for request in requests)
    ]
    if forbidden:
        return False, f"Command used {forbidden}, which the task rules out."

    cursor = 0
    for expected in expectations:
        matched = next(
            (
                index
                for index in range(cursor, len(requests))
                if request_matches(expected, requests[index])
            ),
            None,
        )
        if matched is None:
            return False, (
                "Expected request not found (in order): "
                f"{json.dumps(expected, sort_keys=True)}."
            )
        cursor = matched + 1

    return True, f"{len(expectations) or 'All'} expected request(s) matched."


def describe(request: dict[str, Any]) -> str:
    """One-line rendering of a dry-run request, for failure messages."""
    params = json.dumps(request.get("params"), sort_keys=True)
    body = json.dumps(request.get("body"), sort_keys=True)
    return f"{request.get('method')} {request.get('url')} params={params} body={body}"


def describe_all(requests: list[dict[str, Any]]) -> str:
    """Numbered rendering of every observed request, for failure messages."""
    return "\n".join(f"  - {describe(request)}" for request in requests)
