from __future__ import annotations

import json
import re
import sys

from pathlib import Path
from typing import Any

from .errors import UsageError


def _read_at_ref(ref: str) -> tuple[str, str | None]:
    """Return (content, suffix) for @file refs ('@-' = stdin)."""
    if ref == "@-":
        return sys.stdin.read(), None
    path = Path(ref[1:])
    if not path.is_file():
        raise UsageError(f"Cannot read file: {ref[1:]}", status_code=None)
    return path.read_text(), path.suffix.lower()


def parse_value(raw: str) -> Any:
    if raw.startswith("[") or raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise UsageError(f"Invalid JSON field value: {e}") from e
    return raw


def parse_fields(fields: list[str]) -> dict:
    out: dict[str, Any] = {}
    for item in fields:
        if ":" not in item:
            raise UsageError(f"Invalid --field {item!r}: expected KEY:VALUE")
        key, _, raw = item.partition(":")
        if raw.startswith("@"):
            content, suffix = _read_at_ref(raw)
            if suffix == ".md":
                out[key] = {"format": "db_markdown", "content": content}
            else:
                out[key] = parse_value(content) if suffix == ".json" else content
        else:
            out[key] = parse_value(raw)
    return out


def resolve_page_ref(client: Any, raw: str | int) -> int:
    if isinstance(raw, int) or (isinstance(raw, str) and raw.isdigit()):
        return int(raw)
    result = client.get("/pages/find/", params={"html_path": raw})
    # find answers 302 + Location; transport surfaces {"location": ...}
    loc = result.get("location", "") if isinstance(result, dict) else ""
    match = re.search(r"/pages/(\d+)/", loc)
    if match:
        return int(match.group(1))
    raise UsageError(f"Could not resolve page path: {raw}")
