"""`wt skills`: serve the agent skills bundled with this CLI.

The skills are the same files the documentation site publishes under
``.well-known/agent-skills/``. Serving them here means an agent can load
content that always matches the installed CLI version, rather than a snapshot
it may have downloaded earlier.
"""

from __future__ import annotations

import json
import os

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer

from wagtail_cli.errors import NotFoundError, UsageError, WgtlError

from ._shared import LOCAL_HUMAN_OPTION as _LOCAL_HUMAN_OPTION
from ._shared import LOCAL_JSON_OPTION as _LOCAL_JSON_OPTION
from .main import appify, resolve_output_format


# Bundled with the package: `src/wagtail_cli/.agents/skills/` (see
# `[tool.uv.build-backend]` in pyproject.toml, which keeps dot-directories).
BUNDLED_SKILLS_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills"

SKILLS_DIR_ENV = "WAGTAIL_CLI_SKILLS_DIR"
"""Override the skills directory, for development and tests."""

PREFIX = "cli-"
"""Skill names carry this prefix; the suffix is also accepted as a short alias."""

_REFERENCE_DIRS = ("references", "templates")


@dataclass
class Skill:
    name: str
    description: str
    dir: Path
    hidden: bool
    short_description: str = ""


def _parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse the handful of top-level keys this command needs.

    Deliberately not a YAML parser: a full one would add a runtime dependency
    for two string fields and a boolean.
    """
    meta: dict[str, Any] = {
        "name": "",
        "description": "",
        "short_description": "",
        "hidden": False,
    }
    text = content.lstrip("\ufeff").lstrip()
    if not text.startswith("---"):
        return meta
    rest = text[3:]
    end = rest.find("\n---")
    if end == -1:
        return meta
    lines = rest[:end].splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        key, sep, value = line.partition(":")
        key = key.strip()
        # Only top-level keys; skip blank lines and indented continuations.
        if not sep or line[:1].isspace():
            i += 1
            continue
        value = value.strip()
        if key in ("name", "description"):
            if value in ("", ">", ">-", "|", "|-"):
                parts = []
                j = i + 1
                while j < len(lines) and (
                    not lines[j].strip() or lines[j][:1].isspace()
                ):
                    parts.append(lines[j].strip())
                    j += 1
                meta[key] = " ".join(part for part in parts if part)
                i = j
                continue
            meta[key] = value
        elif key == "hidden":
            meta["hidden"] = value.lower() in ("true", "yes")
        elif key == "metadata":
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j][:1].isspace()):
                sub_key, sub_sep, sub_value = lines[j].strip().partition(":")
                if sub_sep and sub_key.strip() == "short-description":
                    meta["short_description"] = sub_value.strip()
                j += 1
            i = j
            continue
        i += 1
    return meta


def _skills_root() -> Path:
    override = os.environ.get(SKILLS_DIR_ENV)
    return Path(override) if override else BUNDLED_SKILLS_DIR


def _load_skills() -> list[Skill]:
    root = _skills_root()
    if not root.is_dir():
        raise WgtlError(
            f"Skills directory not found: {root}. "
            f"Set {SKILLS_DIR_ENV} or reinstall wagtail-cli."
        )
    skills = []
    for entry in sorted(root.iterdir()):
        skill_md = entry / "SKILL.md"
        if not entry.is_dir() or not skill_md.is_file():
            continue
        meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        skills.append(
            Skill(
                name=meta["name"] or entry.name,
                description=meta["description"],
                dir=entry,
                hidden=meta["hidden"],
                short_description=meta["short_description"],
            )
        )
    return skills


def _aliases(skills: list[Skill]) -> dict[str, str]:
    """Map short names (`api`) to skill names (`cli-api`)."""
    names = {skill.name for skill in skills}
    aliases = {}
    for skill in skills:
        if skill.name.startswith(PREFIX):
            short = skill.name[len(PREFIX) :]
            if short and short not in names and short not in aliases:
                aliases[short] = skill.name
    return aliases


def _resolve(skills: list[Skill], name: str) -> Skill | None:
    aliases = _aliases(skills)
    if name in aliases:
        name = aliases[name]
    for skill in skills:
        if name in (skill.name, skill.dir.name):
            return skill
    return None


def _shorten(text: str, max_len: int = 90) -> str:
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def _emit(ctx: typer.Context, payload: Any, human: str) -> None:
    """Print JSON or human output; JSON is forced by `--json`/`--human`."""
    if _wants_json(ctx):
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        typer.echo(human)


def _wants_json(ctx: typer.Context) -> bool:
    return resolve_output_format(ctx) == "json"


def _reference_files(skill_dir: Path) -> list[tuple[str, str]]:
    """Collect the skill's supplementary files, sorted, as (relative, content)."""
    files = []
    for subdir_name in _REFERENCE_DIRS:
        subdir = skill_dir / subdir_name
        if not subdir.is_dir():
            continue
        for path in sorted(subdir.iterdir()):
            if path.is_file():
                rel = f"{subdir_name}/{path.name}"
                files.append((rel, path.read_text(encoding="utf-8")))
    return files


def _list_skills(ctx: typer.Context) -> None:
    skills = [skill for skill in _load_skills() if not skill.hidden]
    if _wants_json(ctx):
        _emit(
            ctx,
            {
                "skills": [
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "short_description": skill.short_description,
                    }
                    for skill in skills
                ]
            },
            "",
        )
        return
    if not skills:
        typer.echo("No skills found")
        return
    width = max(len(skill.name) for skill in skills)
    for skill in skills:
        summary = skill.short_description or skill.description
        typer.echo(f"{skill.name:<{width}}  {_shorten(summary)}")


def _get_skills(ctx: typer.Context, names: list[str], all_skills: bool, full: bool):
    skills = _load_skills()
    if all_skills:
        targets = [skill for skill in skills if not skill.hidden]
    else:
        if not names:
            raise UsageError("No skill name provided. Usage: wt skills get <name>")
        targets = []
        for name in names:
            skill = _resolve(skills, name)
            if skill is None:
                known = ", ".join(skill.name for skill in skills)
                raise NotFoundError(f"Skill not found: {name} (available: {known})")
            targets.append(skill)

    if _wants_json(ctx):
        payload = []
        for skill in targets:
            entry: dict[str, Any] = {
                "name": skill.name,
                "path": str(skill.dir),
                "content": (skill.dir / "SKILL.md").read_text(encoding="utf-8"),
            }
            if full:
                entry["files"] = [
                    {"path": rel, "content": content}
                    for rel, content in _reference_files(skill.dir)
                ]
            payload.append(entry)
        _emit(ctx, {"skills": payload}, "")
        return

    for index, skill in enumerate(targets):
        if index:
            typer.echo("\n---\n")
        content = (skill.dir / "SKILL.md").read_text(encoding="utf-8")
        typer.echo(content.rstrip("\n"))
        if full:
            for rel, file_content in _reference_files(skill.dir):
                typer.echo(f"\n--- {rel} ---\n")
                typer.echo(file_content.rstrip("\n"))


def _show_path(ctx: typer.Context, name: str | None) -> None:
    skills = _load_skills()
    root = _skills_root()
    if name is None:
        _emit(ctx, {"path": str(root)}, str(root))
        return
    skill = _resolve(skills, name)
    if skill is None:
        raise NotFoundError(f"Skill not found: {name}")
    _emit(ctx, {"name": skill.name, "path": str(skill.dir)}, str(skill.dir))


ALL_OPTION = typer.Option(
    False,
    "--all",
    help="Load every visible skill (excludes the hidden discovery stub).",
)

FULL_OPTION = typer.Option(
    False,
    "--full",
    help="Also print the skill's reference and template files.",
)


skills_app = typer.Typer(
    name="skills",
    help=(
        "Read the agent skills bundled with this CLI. Skills are served from "
        "the installed version, so their instructions always match the CLI."
    ),
    invoke_without_command=True,
    no_args_is_help=False,
)


@skills_app.callback()
@appify
def skills_callback(
    ctx: typer.Context,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
) -> None:
    """List the agent skills bundled with this CLI."""
    if ctx.invoked_subcommand is None:
        _list_skills(ctx)


@skills_app.command(name="list")
@appify
def list_skills(
    ctx: typer.Context,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
) -> None:
    """List the available skills with their descriptions."""
    _list_skills(ctx)


@skills_app.command()
@appify
def get(
    ctx: typer.Context,
    names: list[str] = typer.Argument(  # noqa: B008
        None, help="Skill names, e.g. `cli-api` or the short alias `api`."
    ),
    all_skills: bool = ALL_OPTION,
    full: bool = FULL_OPTION,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
) -> None:
    """Print a skill's SKILL.md, to load its instructions."""
    _get_skills(ctx, names or [], all_skills, full)


@skills_app.command()
@appify
def path(
    ctx: typer.Context,
    name: str | None = typer.Argument(
        None, help="Skill name; with no argument, print the skills directory."
    ),
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
) -> None:
    """Print where a skill's files live on disk."""
    _show_path(ctx, name)


from .main import app  # noqa: E402  # attach the skills group to the root app


app.add_typer(skills_app, name="skills")
