from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import sys

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import typer

from click import Context
from typer.main import get_command

from wagtail_cli import __version__, output
from wagtail_cli.config import load_config
from wagtail_cli.errors import UsageError, WgtlError
from wagtail_cli.resources._client import DryRunRequest, WgtlClient


app = typer.Typer(
    name="wt",
    help="CLI client for the Wagtail v3 API.",
    no_args_is_help=True,
)

api_app = typer.Typer(
    name="api",
    help="Interact with a Wagtail v3 API.",
    no_args_is_help=True,
)

app.add_typer(api_app, name="api")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@dataclass
class CliContext:
    url: str | None = None
    token: str | None = None
    fmt: str | None = None  # "json" | "human" | None (auto)
    verbose: bool = False
    dry_run: bool = False


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    url: str | None = typer.Option(
        None, "--url", help="API base URL (overrides config/env)."
    ),
    token: str | None = typer.Option(
        None, "--token", help="API token (overrides config/env)."
    ),
    json: bool = typer.Option(False, "--json", help="Force JSON output."),
    human: bool = typer.Option(False, "--human", help="Force human-readable output."),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Print HTTP request/response details to stderr.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print the HTTP request that would be sent without sending it.",
    ),
    ctx: typer.Context = typer.Context,
) -> None:
    """CLI client for the Wagtail v3 API."""
    fmt: str | None = None
    if json and human:
        # The root callback is not appify-wrapped, so emit a clean usage error
        # rather than raising (which would surface as an uncaught traceback).
        typer.echo("Error (2): Cannot combine --json and --human", err=True)
        raise typer.Exit(code=2)
    if json:
        fmt = "json"
    elif human:
        fmt = "human"
    ctx.obj = CliContext(
        url=url,
        token=token,
        fmt=fmt,
        verbose=verbose,
        dry_run=dry_run,
    )


def get_client(ctx: typer.Context) -> WgtlClient:
    """Build a configured WgtlClient from global options + config cascade."""
    cc: CliContext = ctx.obj
    cfg = load_config(cli_url=cc.url, cli_token=cc.token)
    if not cfg.is_configured:
        raise UsageError(
            "Not configured. Run `wt init` or set WAGTAIL_CLI_BASE_URL / "
            "WAGTAIL_CLI_TOKEN."
        )
    return WgtlClient(
        cfg.base_url,
        cfg.token,
        dry_run=cc.dry_run,
        verbose=cc.verbose,
    )


def emit(ctx: typer.Context, data: Any) -> None:
    """Render data (or a dry-run request preview) to stdout."""
    cc: CliContext = ctx.obj
    fmt = cc.fmt
    if isinstance(data, DryRunRequest):
        if fmt == "json":
            typer.echo(json.dumps(asdict(data), separators=(",", ":"), default=str))
            return
        lines = [f"{data.method} {data.url}"]
        if data.params:
            lines.append(f"Params: {data.params}")
        if data.body is not None:
            lines.append(json.dumps(data.body, indent=2, default=str))
        if data.file:
            lines.append(f"File: {data.file}")
        typer.echo("\n".join(lines))
        return
    typer.echo(output.render(data, fmt))


def appify(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Map WgtlError to a stderr message + exit code; forward RFC 7807 body."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except WgtlError as e:
            typer.echo(f"Error ({e.status_code or e.exit_code}): {e}", err=True)
            if e.problem is not None:
                body = (
                    json.dumps(e.problem, indent=2, default=str)
                    if isinstance(e.problem, (dict, list))
                    else str(e.problem)
                )
                typer.echo(body, err=True)
            raise typer.Exit(code=e.exit_code) from e

    return wrapper


def cli() -> None:
    """Console entry point: route known groups/globals to Typer, delegate the rest."""
    argv = sys.argv[1:]
    if argv and argv[0] == "--version":
        _print_enhanced_version()
        return
    if argv and argv[0] in ("--help", "-h"):
        _print_enhanced_help()
        return
    first = argv[0] if argv else None
    if not first or first in _KNOWN_GROUPS or first.startswith("-"):
        app()
        return
    # `cli()` is the console entry point and runs outside Typer's runner, so
    # we exit here via SystemExit, not typer.Exit (which is only meaningful
    # inside a Typer command context).
    target = resolve_delegate(argv)
    if target is None:
        typer.echo(
            "Cannot run a Django command here: no ./manage.py in the current "
            "directory and DJANGO_SETTINGS_MODULE is not set.",
            err=True,
        )
        raise SystemExit(1)
    raise SystemExit(subprocess.call(target))  # noqa: S603  # argv is user-authored CLI args forwarded verbatim to the Django runner


_KNOWN_GROUPS = {"api", "start"}


def resolve_delegate(args: list[str]) -> list[str] | None:
    """Resolve the command to run for a delegated invocation.

    Returns the argv to run, or None when there is nothing to delegate to.
    """
    manage_py = Path.cwd() / "manage.py"
    if manage_py.is_file():
        return [sys.executable, str(manage_py), *args]
    if os.environ.get("DJANGO_SETTINGS_MODULE"):
        return ["django-admin", *args]
    return None


def _capture(cmd: list[str]) -> str | None:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603  # explicit argv list, no shell
    except OSError:
        return None
    if proc.returncode == 0:
        return proc.stdout.strip()
    return None


def _print_enhanced_version() -> None:
    typer.echo(f"wagtail-cli {__version__}")
    wagtail_ver = _capture(["wagtail", "--version"])
    if wagtail_ver:
        typer.echo(f"Wagtail: {wagtail_ver}")
    django_ver = _capture(["django-admin", "--version"])
    if django_ver:
        typer.echo(f"Django: {django_ver}")
    raise SystemExit(0)


def _print_enhanced_help() -> None:
    cmd = get_command(app)
    ctx = Context(cmd, info_name="wt")
    typer.echo(cmd.get_help(ctx))
    manage_py = Path.cwd() / "manage.py"
    if manage_py.is_file():
        out = _capture([sys.executable, str(manage_py), "--help"])
        if out:
            typer.echo("\n--- ./manage.py --help ---\n")
            typer.echo(out)
    raise SystemExit(0)


DEFAULT_PROJECT_TEMPLATE = (
    "https://github.com/wagtail/wagtail-custom-base-page-template/archive/main.zip"
)


def build_startproject_args(
    name: str,
    directory: str | None,
    template: str,
    extensions: list[str],
    names: list[str],
    excludes: list[str],
    verbosity: int,
    settings: str | None,
    pythonpath: str | None,
    traceback: bool,
    no_color: bool,
    force_color: bool,
    version: bool,
) -> list[str]:
    args = [
        "django-admin",
        "startproject",
        f"--template={template}",
        "--ext=" + ",".join(extensions),
        "--name=" + ",".join(names),
    ]
    args += [f"--exclude={x}" for x in excludes]
    args.append(name)
    if directory:
        args.append(directory)
    if version:
        args.append("--version")
    if verbosity != 1:
        args += [f"--verbosity={verbosity}"]
    if settings:
        args += [f"--settings={settings}"]
    if pythonpath:
        args += [f"--pythonpath={pythonpath}"]
    if traceback:
        args.append("--traceback")
    if no_color:
        args.append("--no-color")
    if force_color:
        args.append("--force-color")
    return args


@app.command()
def start(
    name: str = typer.Argument(..., help="Name of the application or project."),
    directory: str | None = typer.Argument(
        None, help="Optional destination directory, created if needed."
    ),
    template: str = typer.Option(
        DEFAULT_PROJECT_TEMPLATE,
        "--template",
        help="The path or URL to load the template from.",
    ),
    extension: list[str] = typer.Option(  # noqa: B008
        ["html", "rst"],
        "--extension",
        "-e",
        help="File extension(s) to render (repeatable).",
    ),
    name_files: list[str] = typer.Option(  # noqa: B008
        ["Dockerfile"], "--name", "-n", help="File name(s) to render (repeatable)."
    ),
    exclude: list[str] = typer.Option(  # noqa: B008
        [], "--exclude", "-x", help="Directory name(s) to exclude (repeatable)."
    ),
    verbosity: int = typer.Option(
        1, "-v", "--verbosity", min=0, max=3, help="Verbosity level 0-3."
    ),
    settings: str | None = typer.Option(
        None, "--settings", help="Python path to settings module."
    ),
    pythonpath: str | None = typer.Option(
        None, "--pythonpath", help="Directory to add to PYTHONPATH."
    ),
    traceback: bool = typer.Option(
        False, "--traceback", help="Show full traceback on CommandError."
    ),
    no_color: bool = typer.Option(False, "--no-color", help="Don't colorize output."),
    force_color: bool = typer.Option(
        False, "--force-color", help="Force colorized output."
    ),
    version: bool = typer.Option(
        False, "--version", help="Show Django startproject version and exit."
    ),
) -> None:
    """Create a Django project directory structure (replicates `wagtail start`)."""
    try:
        __import__(name)
    except ImportError:
        pass
    else:
        typer.echo(
            f"'{name}' conflicts with the name of an existing Python module "
            "and cannot be used as a project name. Please try another name.",
            err=True,
        )
        raise typer.Exit(code=1)

    template_display = template
    if template == DEFAULT_PROJECT_TEMPLATE:
        template_display = "the default custom base page template"
    typer.echo(f"Creating a Wagtail project called {name} using {template_display}")

    if not shutil.which("django-admin"):
        typer.echo(
            "django-admin not found on PATH. Install Django to create a project "
            "(e.g. `pip install Django`).",
            err=True,
        )
        raise typer.Exit(code=1)

    argv = build_startproject_args(
        name,
        directory,
        template,
        extension,
        name_files,
        exclude,
        verbosity,
        settings,
        pythonpath,
        traceback,
        no_color,
        force_color,
        version,
    )
    raise SystemExit(subprocess.run(argv).returncode)  # noqa: S603  # argv is user-authored CLI args forwarded verbatim to django-admin
