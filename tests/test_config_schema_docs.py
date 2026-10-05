"""Tests for the published .wagtail-cli.toml JSON Schema in the docs site.

The schema is a static file under ``docs/schema/``, which MkDocs copies into
the built site verbatim (non-Markdown files in ``docs_dir`` are copied as-is).
These tests guard the properties that make that work: the file lives in the
docs source tree and its ``$id`` matches the URL we document.
"""

import json

from pathlib import Path


ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
SCHEMA_PATH = DOCS_DIR / "schema" / "wagtail-cli.json"
SCHEMA_URL = "https://wagtail.github.io/wagtail-cli/schema/wagtail-cli.json"


def test_schema_lives_in_the_docs_source_tree():
    # MkDocs only publishes files under docs_dir; anything outside is dropped
    # from the site without warning.
    assert SCHEMA_PATH.exists()


def test_schema_publishes_at_the_documented_url():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    # docs/schema/x.json is served from /schema/x.json under site_url, so the
    # schema's own $id must match that absolute URL.
    site_root = "https://wagtail.github.io/wagtail-cli"
    rel = SCHEMA_PATH.relative_to(DOCS_DIR).as_posix()
    assert schema["$id"] == f"{site_root}/{rel}"
    assert schema["$id"] == SCHEMA_URL
