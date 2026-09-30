from __future__ import annotations

import typer

from wagtail_cli.config import Config, save_user_config
from wagtail_cli.resources._client import WgtlClient

from ._shared import LOCAL_DRY_RUN_OPTION as _LOCAL_DRY_RUN_OPTION
from ._shared import LOCAL_HUMAN_OPTION as _LOCAL_HUMAN_OPTION
from ._shared import LOCAL_JSON_OPTION as _LOCAL_JSON_OPTION
from ._shared import SELECT_OPTION as _SELECT_OPTION
from .main import (
    api_app,
    appify,
    emit,
    get_cli_context,
    get_client,
    is_dry_run,
)


@api_app.command(name="whoami")
@appify
def whoami(
    ctx: typer.Context,
    select: list[str] | None = _SELECT_OPTION,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
    dry_run: bool = _LOCAL_DRY_RUN_OPTION,
) -> None:
    """Show the authenticated user for the current session."""
    client = get_client(ctx)
    emit(ctx, client.get("/whoami/"), select=select)


@api_app.command(name="init")
@appify
def init(
    ctx: typer.Context,
    url: str | None = typer.Option(
        None, "--url", help="API base URL (skips the prompt)."
    ),
    token: str | None = typer.Option(
        None, "--token", help="API token (skips the prompt)."
    ),
    dry_run: bool = _LOCAL_DRY_RUN_OPTION,
) -> None:
    """Configure credentials interactively and save them to ~/.wagtail-cli.toml."""
    cc = get_cli_context(ctx)
    url = url or cc.url
    token = token or cc.token

    if not url:
        url = typer.prompt(
            "Wagtail API base URL",
            default="https://cms.example.com/api/v3/",
        )
    if not token:
        token = typer.prompt("API token", hide_input=True)

    if not url or not token:
        typer.echo("URL and token are both required.", err=True)
        raise typer.Exit(code=2)

    dry_run = is_dry_run(ctx)
    # Test the connection directly (never via get_client, which requires full
    # config). init may legitimately be run without prior config.
    client = WgtlClient(url, token, dry_run=dry_run, verbose=cc.verbose)
    data = client.get("/whoami/")

    username = None
    if isinstance(data, dict) and isinstance(data.get("user"), dict):
        username = data.get("user", {}).get("username")

    if dry_run:
        redacted = (token[:4] + "…") if token else ""
        typer.echo(
            f"dry-run: would write token for url={url} (token={redacted}) "
            "to ~/.wagtail-cli.toml. No file was written; no connection was made."
        )
        return

    save_user_config(Config(base_url=url, token=token))
    who = f" as {username}" if username else ""
    typer.echo(f"Connected. Config written to ~/.wagtail-cli.toml{who}.")
