from __future__ import annotations

import json
import sys

from typing import Any


def _stdout_is_tty() -> bool:
    return sys.stdout.isatty()


def render(
    data: Any,
    fmt: str | None = None,
    select: list[str] | tuple[str, ...] | None = None,
) -> str:
    if select:
        data = project(data, select)
    if fmt is None:
        fmt = "human" if _stdout_is_tty() else "json"
    if fmt == "json":
        return json.dumps(data, separators=(",", ":"), default=str)
    return _human(data)


def project(data: Any, selectors: list[str] | tuple[str, ...]) -> Any:
    """Project response data onto dot-separated fields.

    Collection responses keep their pagination count while selectors apply to
    each item. This is intentionally a local projection: the v3 API does not
    support ``fields=`` projections, but agents often only need an id, title,
    URL, or status from a large response.
    """
    selectors = tuple(
        part.strip() for value in selectors for part in value.split(",") if part.strip()
    )
    if not selectors:
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        projected: dict[str, Any] = {
            key: data[key] for key in ("count", "next", "previous") if key in data
        }
        projected["items"] = [_project_item(item, selectors) for item in data["items"]]
        return projected
    if isinstance(data, list):
        return [_project_item(item, selectors) for item in data]
    return _project_item(data, selectors)


def _project_item(item: Any, selectors: tuple[str, ...]) -> Any:
    if not isinstance(item, dict):
        return item
    projected: dict[str, Any] = {}
    for selector in selectors:
        parts = tuple(part for part in selector.split(".") if part)
        if not parts:
            continue
        _set_path(projected, parts, _get_path(item, parts))
    return projected


def _get_path(data: dict[str, Any], parts: tuple[str, ...]) -> Any:
    value: Any = data
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _set_path(data: dict[str, Any], parts: tuple[str, ...], value: Any) -> None:
    target = data
    for part in parts[:-1]:
        child = target.get(part)
        if not isinstance(child, dict):
            child = {}
            target[part] = child
        target = child
    target[parts[-1]] = value


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
