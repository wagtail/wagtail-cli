"""Tests for the docs-site skill publication.

Only `wagtail` lives in `.agents/skills/`, so it is the only skill published to
the discovery index. Everything else lives in `skill-data/` and is bundled for
the CLI to serve on demand (`wt skills get`).
"""

import importlib.util
import json

from pathlib import Path


HOOKS_PATH = Path(__file__).resolve().parent.parent / "docs" / "hooks.py"
_spec = importlib.util.spec_from_file_location("docs_hooks", HOOKS_PATH)
assert _spec and _spec.loader
hooks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hooks)


def test_only_wagtail_is_published(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    hooks.on_post_build(
        {"site_dir": str(site), "site_url": "https://example.test/wagtail-cli"}
    )

    published = site / ".well-known" / "agent-skills"
    assert (published / "wagtail" / "SKILL.md").is_file()
    assert not (published / "cli-api").exists()
    assert not (published / "cli-docs").exists()

    index = json.loads((published / "index.json").read_text(encoding="utf-8"))
    assert [skill["name"] for skill in index["skills"]] == ["wagtail"]

    catalog = json.loads(
        (site / ".well-known" / "ai-catalog.json").read_text(encoding="utf-8")
    )
    published_names = [
        entry["identifier"].rsplit(":", 1)[-1] for entry in catalog["entries"]
    ]
    assert published_names == ["wagtail"]
