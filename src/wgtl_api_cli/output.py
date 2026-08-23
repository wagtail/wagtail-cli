from __future__ import annotations

import json
import sys

from typing import Any


def _stdout_is_tty() -> bool:
    return sys.stdout.isatty()


def render(data: Any, fmt: str | None = None) -> str:
    if fmt is None:
        fmt = "human" if _stdout_is_tty() else "json"
    if fmt == "json":
        return json.dumps(data, separators=(",", ":"), default=str)
    return _human(data)


def _human(data: Any) -> str:
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return _table(data["items"]) or "(no results)"
    if isinstance(data, dict):
        return "\n".join(f"{k}: {_scalar(v)}" for k, v in data.items())
    if isinstance(data, list):
        return _table(data) or "(no results)"
    return str(data)


def _scalar(v: Any) -> str:
    if isinstance(v, (dict, list)):
        return json.dumps(v, default=str)
    return "null" if v is None else str(v)


_FLATTEN_PREFS = ("id", "title", "name", "label")


def _table(items: list[Any]) -> str:
    rows = [i if isinstance(i, dict) else {"value": i} for i in items]
    # flatten one level of nested meta
    flat = []
    for r in rows:
        row = {k: v for k, v in r.items() if k != "meta"}
        meta = r.get("meta") or {}
        if isinstance(meta, dict):
            for mk, mv in meta.items():
                if isinstance(mv, (str, int, bool)) or mv is None:
                    row[f"meta.{mk}"] = mv
        flat.append(row)
    keys: list[str] = list(dict.fromkeys(k for r in flat for k in r))[:6]
    widths = {k: max(len(k), *(len(_scalar(r.get(k))) for r in flat)) for k in keys}
    header = "  ".join(k.ljust(widths[k]) for k in keys)
    lines = [header]
    for r in flat:
        lines.append("  ".join(_scalar(r.get(k)).ljust(widths[k]) for k in keys))
    return "\n".join(lines)
