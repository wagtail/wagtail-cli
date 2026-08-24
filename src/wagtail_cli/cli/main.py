from __future__ import annotations

import functools
import json

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

import typer

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
            "Not configured. Run `wt init` or set WAGTAIL_CLI_BASE_URL / \
            WAGTAIL_CLI_TOKEN."
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
    """Console entry point (Typer app)."""
    app()
