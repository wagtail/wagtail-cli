"""Tests for `wt skills`: listing, loading, aliases, and path reporting."""

import json

from pathlib import Path

import pytest

from typer.testing import CliRunner

from wagtail_cli.cli.main import app


runner = CliRunner()


def _write_skill(
    root: Path,
    name: str,
    body: str,
    *,
    description: str = "A skill.",
    short_description: str | None = None,
    hidden: bool = False,
    references: dict[str, str] | None = None,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    metadata = ""
    if short_description:
        metadata = f"metadata:\n  short-description: {short_description}\n"
    hidden_line = "hidden: true\n" if hidden else ""
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: >-\n  {description}\n"
        f"{hidden_line}{metadata}---\n\n{body}\n",
        encoding="utf-8",
    )
    for rel, content in (references or {}).items():
        reference = skill_dir / rel
        reference.parent.mkdir(parents=True, exist_ok=True)
        reference.write_text(content, encoding="utf-8")
    return skill_dir


@pytest.fixture
def skills_dir(tmp_path, monkeypatch):
    root = tmp_path / "skills"
    _write_skill(
        root,
        "cli-api",
        "# API skill\n\nOperate a site.\n",
        short_description="Operate a Wagtail site",
        references={"references/commands.md": "commands reference\n"},
    )
    _write_skill(
        root,
        "cli-docs",
        "# Docs skill\n\nRead the docs.\n",
        short_description="Read the docs",
    )
    _write_skill(
        root,
        "wagtail",
        "# Stub\n\nRun `wt skills get`.\n",
        description=(
            "Broad trigger for Wagtail tasks, e.g. operating a site or reading "
            "documentation."
        ),
        hidden=True,
    )
    monkeypatch.setenv("WAGTAIL_CLI_SKILLS_DIR", str(root))
    return root


# --- list ---


def test_skills_lists_visible_skills(skills_dir):
    result = runner.invoke(app, ["skills"])
    assert result.exit_code == 0
    assert "cli-api" in result.output
    assert "cli-docs" in result.output


def test_skills_hides_hidden_stub_from_list(skills_dir):
    result = runner.invoke(app, ["skills", "list"])
    assert result.exit_code == 0
    assert "wagtail " not in result.output
    assert "wagtail\n" not in result.output


def test_skills_list_json(skills_dir):
    result = runner.invoke(app, ["skills", "list", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert [skill["name"] for skill in payload["skills"]] == [
        "cli-api",
        "cli-docs",
    ]
    assert payload["skills"][0]["short_description"] == "Operate a Wagtail site"


def test_skills_list_global_json(skills_dir):
    result = runner.invoke(app, ["--json", "skills", "list"])
    assert result.exit_code == 0
    assert json.loads(result.output)["skills"]


def test_skills_local_human_overrides_global_json(skills_dir):
    result = runner.invoke(app, ["--json", "skills", "list", "--human"])
    assert result.exit_code == 0
    assert not result.output.startswith("{")


def test_skills_list_json_human_conflict(skills_dir):
    result = runner.invoke(app, ["skills", "list", "--json", "--human"])
    assert result.exit_code == 2


# --- get ---


def test_skills_get_by_name(skills_dir):
    result = runner.invoke(app, ["skills", "get", "cli-api"])
    assert result.exit_code == 0
    assert "name: cli-api" in result.output
    assert "# API skill" in result.output


def test_skills_get_short_alias(skills_dir):
    result = runner.invoke(app, ["skills", "get", "docs"])
    assert result.exit_code == 0
    assert "name: cli-docs" in result.output


def test_skills_get_hidden_skill_by_name(skills_dir):
    result = runner.invoke(app, ["skills", "get", "wagtail"])
    assert result.exit_code == 0
    assert "Run `wt skills get`" in result.output


def test_skills_get_all_excludes_hidden(skills_dir):
    result = runner.invoke(app, ["skills", "get", "--all"])
    assert result.exit_code == 0
    assert "name: cli-api" in result.output
    assert "name: cli-docs" in result.output
    assert "name: wagtail\n" not in result.output


def test_skills_get_multiple_separated(skills_dir):
    result = runner.invoke(app, ["skills", "get", "api", "docs"])
    assert result.exit_code == 0
    assert "\n---\n" in result.output
    assert result.output.index("# API skill") < result.output.index("# Docs skill")


def test_skills_get_full_includes_references(skills_dir):
    result = runner.invoke(app, ["skills", "get", "api", "--full"])
    assert result.exit_code == 0
    assert "--- references/commands.md ---" in result.output
    assert "commands reference" in result.output


def test_skills_get_json_full_files(skills_dir):
    result = runner.invoke(app, ["skills", "get", "api", "--full", "--json"])
    assert result.exit_code == 0
    skill = json.loads(result.output)["skills"][0]
    assert skill["name"] == "cli-api"
    assert skill["files"] == [
        {"path": "references/commands.md", "content": "commands reference\n"}
    ]


def test_skills_get_json_omits_files_without_full(skills_dir):
    result = runner.invoke(app, ["skills", "get", "api", "--json"])
    assert "files" not in json.loads(result.output)["skills"][0]


def test_skills_get_unknown_skill(skills_dir):
    result = runner.invoke(app, ["skills", "get", "nope"])
    assert result.exit_code == 6
    assert "Skill not found: nope" in result.stderr


def test_skills_get_unknown_skill_json_error(skills_dir):
    result = runner.invoke(app, ["skills", "get", "nope", "--json"])
    assert result.exit_code == 6
    assert json.loads(result.stderr)["error"]["code"] == 6


def test_skills_get_without_name(skills_dir):
    result = runner.invoke(app, ["skills", "get"])
    assert result.exit_code == 2
    assert "No skill name" in result.stderr


# --- path ---


def test_skills_path_root(skills_dir):
    result = runner.invoke(app, ["skills", "path"])
    assert result.exit_code == 0
    assert result.output.strip() == str(skills_dir)


def test_skills_path_named(skills_dir):
    result = runner.invoke(app, ["skills", "path", "api"])
    assert result.exit_code == 0
    assert result.output.strip() == str(skills_dir / "cli-api")


def test_skills_path_named_json(skills_dir):
    result = runner.invoke(app, ["skills", "path", "api", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["name"] == "cli-api"
    assert payload["path"] == str(skills_dir / "cli-api")


def test_skills_path_unknown(skills_dir):
    result = runner.invoke(app, ["skills", "path", "nope"])
    assert result.exit_code == 6


# --- missing directory ---


def test_skills_missing_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGTAIL_CLI_SKILLS_DIR", str(tmp_path / "absent"))
    result = runner.invoke(app, ["skills", "list"])
    assert result.exit_code == 1
    assert "Skills directory not found" in result.stderr


# --- bundled skills ---


def test_bundled_wagtail_stub_is_hidden(monkeypatch):
    """The shipped `wagtail` stub exists, is loadable, and stays out of `list`."""
    monkeypatch.delenv("WAGTAIL_CLI_SKILLS_DIR", raising=False)
    listed = runner.invoke(app, ["skills", "list"])
    assert listed.exit_code == 0
    assert "cli-api" in listed.output
    assert "cli-docs" in listed.output

    stub = runner.invoke(app, ["skills", "get", "wagtail"])
    assert stub.exit_code == 0
    assert "wt skills get cli-api" in stub.output
    assert "discovery stub" in stub.output
