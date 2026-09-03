"""Resolve, fetch, and render docs.wagtail.org content.

Pure logic shared by the `wt docs` commands: URL resolution, Wagtail
version detection, API reference parsing, and search result formatting.
"""

from __future__ import annotations

import importlib.metadata
import json
import re

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit


DEFAULT_DOCS_URL = "https://docs.wagtail.org"
DEFAULT_LANGUAGE = "en"
DOCS_URL_ENV_VAR = "WAGTAIL_CLI_DOCS_URL"

REFERENCE_PATH = "advanced_topics/api/v3/reference.html"
SEARCH_PATH = "_/api/v3/search/"

_VERSION_SEGMENT_RE = re.compile(r"^(?:stable|latest|v?\d+(?:\.\d+){0,2})$")
_WAGTAIL_VERSION_RE = re.compile(r"^(\d+\.\d+)")
_API_PREFIX_RE = re.compile(r"^(?:cms-api|api)/(?:v3(?:-preview)?)/")
_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
_OPERATION_HEADING_RE = re.compile(r"^### (\w+) (/\S+)\s*$")


def resolve_docs_url(
    cli_url: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Resolve the docs site root: CLI flag > WAGTAIL_CLI_DOCS_URL > default."""
    if cli_url:
        return cli_url.rstrip("/")
    if environ is None:
        import os

        environ = os.environ
    env_url = environ.get(DOCS_URL_ENV_VAR)
    if env_url:
        return env_url.rstrip("/")
    return DEFAULT_DOCS_URL


def normalize_wagtail_version(raw: str) -> str | None:
    """Reduce a package version (8.0.1, 8.0b1) to its docs version (8.0)."""
    match = _WAGTAIL_VERSION_RE.match(raw)
    return match.group(1) if match else None


def detect_wagtail_version() -> str | None:
    """Return the docs version of the locally installed Wagtail, if any."""
    try:
        raw = importlib.metadata.version("wagtail")
    except importlib.metadata.PackageNotFoundError:
        return None
    return normalize_wagtail_version(raw)


class _Unset:
    def __repr__(self) -> str:  # pragma: no cover
        return "<unset>"


_unset = _Unset()


def resolve_version(
    explicit: str | None = None,
    installed: str | None | object = _unset,
) -> str:
    """Resolve the docs version to use: --version > local Wagtail > stable."""
    if explicit:
        return explicit
    if installed is _unset:
        installed = detect_wagtail_version()
    return installed if isinstance(installed, str) else "stable"


def resolve_page_url(docs_url: str, language: str, version: str, path: str) -> str:
    """Resolve a user-provided docs path or URL to a Markdown page URL.

    Accepts full URLs (any host, e.g. PR preview builds), paths starting with
    a language or version segment, and bare page paths which get the resolved
    version inserted. A missing .html extension is appended, and the
    .html.md Markdown variant is fetched.
    """
    docs_url = docs_url.rstrip("/")

    if path.startswith(("http://", "https://")):
        url, _, _fragment = path.partition("#")
        parsed = urlsplit(url)
        if parsed.path in ("", "/"):
            # Scheme + host only (e.g. a PR build root): treat as a docs base.
            root = f"{parsed.scheme}://{parsed.netloc}"
            return resolve_page_url(root, language, version, "")
        return _to_markdown_url(url)

    path, _, _fragment = path.partition("#")
    segments = [segment for segment in path.strip().strip("/").split("/") if segment]
    if not segments:
        segments = ["index.html"]

    if (
        segments[0] == language
        and len(segments) > 1
        and _VERSION_SEGMENT_RE.match(segments[1])
    ):
        version, page_segments = segments[1], segments[2:]
    elif _VERSION_SEGMENT_RE.match(segments[0]):
        version, page_segments = segments[0], segments[1:]
    else:
        page_segments = segments

    if not page_segments:
        page_segments = ["index.html"]
    page = "/".join(page_segments)
    if page.endswith(".md"):
        return f"{docs_url}/{language}/{version}/{page}"
    if not page.endswith(".html"):
        page += ".html"
    return f"{docs_url}/{language}/{version}/{page}.md"


def _to_markdown_url(url: str) -> str:
    is_directory = url.endswith("/")
    url = url.rstrip("/")
    if url.endswith(".md"):
        return url
    if url.endswith(".html"):
        return url + ".md"
    if is_directory:
        # Directory-style URL: resolve to the index page, like the bare-path
        # branch does.
        return url + "/index.html.md"
    return url + ".html.md"


def extract_index_section(markdown: str) -> str:
    """Return the content under the `## Index` heading of a docs page."""
    lines = markdown.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Index":
            start = i + 1
            break
    if start is None:
        raise ValueError("No '## Index' section found in the docs index page.")
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


@dataclass
class Operation:
    """One `### METHOD /api/v3/.../` section of the v3 API reference."""

    method: str
    path: str
    heading: str
    body: str

    @property
    def normalized_path(self) -> str:
        return normalize_operation_path(self.path)


def parse_operations(markdown: str) -> list[Operation]:
    """Split the API reference Markdown into per-operation sections."""
    lines = markdown.splitlines()
    headings = [
        (i, match.group(1), match.group(2))
        for i, line in enumerate(lines)
        if (match := _OPERATION_HEADING_RE.match(line))
    ]
    operations = []
    for n, (line_no, method, path) in enumerate(headings):
        body_end = headings[n + 1][0] if n + 1 < len(headings) else len(lines)
        body = "\n".join(lines[line_no + 1 : body_end]).strip()
        operations.append(
            Operation(method=method, path=path, heading=f"{method} {path}", body=body)
        )
    return operations


def normalize_operation_path(path: str) -> str:
    """Reduce an API path to its resource suffix, without version prefixes."""
    normalized = path.strip().strip("/")
    while True:
        stripped = _API_PREFIX_RE.sub("", normalized)
        if stripped == normalized:
            break
        normalized = stripped
    return normalized.strip("/")


def find_operations(
    operations: list[Operation],
    query: str,
) -> tuple[list[Operation], list[Operation]]:
    """Match a query like `GET /api/v3/documents/` against parsed operations.

    Returns (exact_matches, similar_matches). The query's leading HTTP method
    (case-insensitive, optional) narrows the match; the API version prefix is
    optional and `/api/v3/`, `/api/v3-preview/`, and `/cms-api/v3/` all
    normalize to the same resource suffix.
    """
    tokens = query.split()
    method = None
    if tokens and tokens[0].upper() in _HTTP_METHODS:
        method = tokens.pop(0).upper()
    elif len(tokens) > 1 and tokens[-1].upper() in _HTTP_METHODS:
        method = tokens.pop().upper()
    query_path = normalize_operation_path(" ".join(tokens))

    exact = []
    similar = []
    for op in operations:
        method_matches = method is None or method == op.method
        if not method_matches:
            continue
        if query_path == op.normalized_path:
            exact.append(op)
        elif query_path and _path_segments_match(query_path, op.normalized_path):
            similar.append(op)
    return exact, similar


def _path_segments_match(query_path: str, op_path: str) -> bool:
    """Whether query path segments appear in order in the operation path.

    Segment matching tolerates placeholder differences: `{page_id}` matches
    another placeholder name or a literal id like `42`.
    """
    query_segments = query_path.split("/")
    op_segments = op_path.split("/")
    cursor = 0
    for q_seg in query_segments:
        while cursor < len(op_segments) and not _segments_match(
            q_seg, op_segments[cursor]
        ):
            cursor += 1
        if cursor == len(op_segments):
            return False
        cursor += 1
    return True


def _segments_match(q_seg: str, op_seg: str) -> bool:
    if q_seg == op_seg:
        return True
    if op_seg.startswith("{") and (q_seg.startswith("{") or q_seg.isdigit()):
        return True
    return False


def format_search_results(payload: Mapping) -> str:
    """Render a search API response as a concise numbered list."""
    results = payload.get("results", [])
    count = payload.get("count", len(results))
    query = payload.get("query", "")
    if not results:
        return f"No results for {query!r}."
    lines = [f"{count} result{'s' if count != 1 else ''} for {query!r}:", ""]
    for i, result in enumerate(results, start=1):
        lines.append(f"{i}. {result.get('title', '(untitled)')}")
        lines.append(f"   {result.get('path', '')}")
        snippet = _first_snippet(result.get("blocks", []))
        if snippet:
            lines.append(f"   {snippet}")
    return "\n".join(lines)


_SNIPPET_MAX_CHARS = 200


def _first_snippet(blocks: list) -> str:
    for block in blocks:
        content = " ".join(str(block.get("content", "")).split())
        if content:
            if len(content) > _SNIPPET_MAX_CHARS:
                content = content[: _SNIPPET_MAX_CHARS - 1].rstrip() + "…"
            return content
    return ""


def search_payload_to_json(payload: Mapping) -> str:
    """Serialize a search API response for --json output."""
    return json.dumps(payload, indent=2)
