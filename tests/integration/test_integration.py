"""Integration tests for the wt CLI against a live Wagtail v3 API.

These exercise the real CLI (via Typer's ``CliRunner``) end to end against a
live server. They are skipped unless both ``WAGTAIL_CLI_TEST_BASE_URL`` and
``WAGTAIL_CLI_TEST_TOKEN`` are set.

Example (local bakerydemo dev server):
    WAGTAIL_CLI_TEST_BASE_URL=http://127.0.0.1:9001/api/v3 \\
    WAGTAIL_CLI_TEST_TOKEN=wagtail_… uv run pytest -m integration -q
"""

from __future__ import annotations

import base64
import os
import uuid

from pathlib import Path

import pytest

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


BASE_URL = os.environ.get("WAGTAIL_CLI_TEST_BASE_URL")
TOKEN = os.environ.get("WAGTAIL_CLI_TEST_TOKEN")

pytestmark = pytest.mark.integration

if not BASE_URL or not TOKEN:
    pytest.skip(
        "WAGTAIL_CLI_TEST_BASE_URL / WAGTAIL_CLI_TEST_TOKEN not set; skipping integration tests",
        allow_module_level=True,
    )

runner = CliRunner()

# bakerydemo page type with a clean create (only meta + title required; no
# bakerydemo-specific relationship constraints). See task report for why we do
# not use blog.BlogPage (its image_id is gated behind an unrelated required
# blog_person_relationship on the bakerydemo content model).
PAGE_TYPE = "breads.BreadPage"
PARENT_PATH = "/breads/"

# 1x1 red PNG (also used by the image upload scenario).
_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

# bakerydemo's custom image model requires a collection_id (Root = 1) even
# though the OpenAPI create schema marks it optional — see task report.
IMAGE_FIELDS = ["collection_id:1"]


def _invoke(args: list[str]) -> object:
    """Run the CLI with the integration env config and return the result."""
    return runner.invoke(
        app,
        ["api", *args],
        env={"WAGTAIL_CLI_BASE_URL": BASE_URL, "WAGTAIL_CLI_TOKEN": TOKEN},
    )


def _json(result: object) -> dict:
    import json

    return json.loads(result.output)


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def test_whoami_success() -> None:
    result = _invoke(["--json", "whoami"])
    assert result.exit_code == 0, result.output
    data = _json(result)
    assert "user" in data
    assert data["user"]["username"]


def test_pages_list_shape() -> None:
    result = _invoke(["--json", "pages", "list", "--limit", "5"])
    assert result.exit_code == 0, result.output
    data = _json(result)
    assert "count" in data
    assert "items" in data
    assert isinstance(data["count"], int)
    assert isinstance(data["items"], list)


def test_bad_token_exit_4() -> None:
    result = _invoke(["--token", "definitely-not-a-real-token", "whoami"])
    assert result.exit_code == 4
    assert "401" in result.output or "Unauthorized" in result.output


def test_image_upload_lifecycle(tmp_path: Path) -> None:
    """Upload an image, fetch it, then delete it (finally-guarded)."""
    image_id = None
    title = _unique("wt-int-img")
    path = tmp_path / "pic.png"
    path.write_bytes(_PNG)
    try:
        result = _invoke(
            [
                "--json",
                "images",
                "create",
                str(path),
                "--title",
                title,
                "--field",
                *IMAGE_FIELDS,
            ]
        )
        assert result.exit_code == 0, result.output
        data = _json(result)
        image_id = data["id"]
        assert data["title"] == title

        got = _invoke(["--json", "images", "get", str(image_id)])
        assert got.exit_code == 0, got.output
        assert _json(got)["id"] == image_id
    finally:
        if image_id is not None:
            # images delete may prompt unless --yes in a non-TTY.
            _invoke(["images", "delete", str(image_id), "--yes"])


def test_page_lifecycle() -> None:
    """create → get → update → publish → revisions → unpublish → delete."""
    page_id = None
    title = _unique("wt-int-page")
    try:
        # create as a draft
        result = _invoke(
            [
                "--json",
                "pages",
                "create",
                PAGE_TYPE,
                "--parent",
                PARENT_PATH,
                "--title",
                title,
            ]
        )
        assert result.exit_code == 0, result.output
        page_id = _json(result)["id"]

        # get
        got = _invoke(["--json", "pages", "get", str(page_id)])
        assert got.exit_code == 0, got.output
        assert _json(got)["id"] == page_id

        # update (non-TTY requires --yes)
        new_title = title + "-renamed"
        updated = _invoke(
            ["--json", "pages", "update", str(page_id), "--title", new_title, "--yes"]
        )
        assert updated.exit_code == 0, updated.output
        assert _json(updated)["title"] == new_title

        # publish
        published = _invoke(["--json", "pages", "publish", str(page_id)])
        assert published.exit_code == 0, published.output
        assert _json(published)["meta"]["first_published_at"] is not None

        # revisions
        revs = _invoke(["--json", "pages", "revisions", "list", str(page_id)])
        assert revs.exit_code == 0, revs.output
        assert _json(revs)["count"] >= 1

        # unpublish (no --yes gate)
        unpublished = _invoke(["--json", "pages", "unpublish", str(page_id)])
        assert unpublished.exit_code == 0, unpublished.output
    finally:
        if page_id is not None:
            _invoke(["pages", "delete", str(page_id), "--yes"])


def test_dry_run_makes_no_changes() -> None:
    """A --dry-run create must not change the page count."""
    before = _invoke(["--json", "pages", "list", "--limit", "1"])
    assert before.exit_code == 0, before.output
    count_before = _json(before)["count"]

    dry = _invoke(
        [
            "--dry-run",
            "pages",
            "create",
            PAGE_TYPE,
            "--parent",
            PARENT_PATH,
            "--title",
            _unique("wt-dry"),
        ]
    )
    assert dry.exit_code == 0, dry.output
    assert "POST" in dry.output

    after = _invoke(["--json", "pages", "list", "--limit", "1"])
    assert after.exit_code == 0, after.output
    assert _json(after)["count"] == count_before
