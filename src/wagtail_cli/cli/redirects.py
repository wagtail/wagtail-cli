from __future__ import annotations

import typer

from wagtail_cli import parsing
from wagtail_cli.errors import UsageError
from wagtail_cli.resources import redirects as redirects_resources

from ._shared import require_yes as _require_yes
from .main import app, appify, emit, get_client


redirects_app = typer.Typer(
    name="redirects",
    help="List, view, create, and manage redirects.",
    no_args_is_help=True,
)


@redirects_app.command("list")
@appify
def list_redirects(
    ctx: typer.Context,
    order: str | None = typer.Option(
        None, "--order", help="Sort field (prefix - to reverse)."
    ),
    limit: int | None = typer.Option(None, "--limit", help="Maximum items per page."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List redirects."""
    client = get_client(ctx)
    emit(
        ctx,
        redirects_resources.list_redirects(
            client, order=order, limit=limit, offset=offset
        ),
    )


@redirects_app.command("find")
@appify
def find_redirect(
    ctx: typer.Context,
    id: str | None = typer.Option(None, "--id", help="Find by redirect ID."),
    path: str | None = typer.Option(None, "--path", help="Find by old path."),
) -> None:
    """Locate a redirect by ID or old path, returning its API location."""
    if id is None and path is None:
        raise UsageError("Provide one of --id or --path to find a redirect.")
    client = get_client(ctx)
    result = redirects_resources.find_redirect(client, id=id, html_path=path)
    emit(ctx, result)


@redirects_app.command("get")
@appify
def get_redirect(
    ctx: typer.Context,
    redirect_id: int = typer.Argument(help="Redirect ID."),
) -> None:
    """Fetch a single redirect by ID."""
    client = get_client(ctx)
    emit(ctx, redirects_resources.get_redirect(client, redirect_id))


@redirects_app.command("create")
@appify
def create_redirect(
    ctx: typer.Context,
    field: list[str] = typer.Option(  # noqa: B008
        ..., "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Create a redirect. Required field: old_path."""
    client = get_client(ctx)
    result = redirects_resources.create_redirect(client, parsing.parse_fields(field))
    emit(ctx, result)


@redirects_app.command("update")
@appify
def update_redirect(
    ctx: typer.Context,
    redirect_id: int = typer.Argument(help="Redirect ID."),
    field: list[str] = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update a redirect (PUT — old_path required)."""
    if not _require_yes(ctx, yes, f"update redirect {redirect_id}"):
        return
    client = get_client(ctx)
    emit(
        ctx,
        redirects_resources.update_redirect(
            client, redirect_id, parsing.parse_fields(field or [])
        ),
    )


@redirects_app.command("delete")
@appify
def delete_redirect(
    ctx: typer.Context,
    redirect_id: int = typer.Argument(help="Redirect ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a redirect (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete redirect {redirect_id}"):
        return
    client = get_client(ctx)
    emit(ctx, redirects_resources.delete_redirect(client, redirect_id))


app.add_typer(redirects_app, name="redirects")
