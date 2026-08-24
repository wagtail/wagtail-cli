from __future__ import annotations

import typer

from wagtail_cli import parsing
from wagtail_cli.resources import sites as sites_resources

from ._shared import is_tty as _is_tty  # noqa: F401
from ._shared import require_yes as _require_yes
from .main import app, appify, emit, get_client


sites_app = typer.Typer(
    name="sites",
    help="List, view, create, and manage sites.",
    no_args_is_help=True,
)


@sites_app.command("list")
@appify
def list_sites(
    ctx: typer.Context,
    limit: int | None = typer.Option(None, "--limit", help="Maximum items per page."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List sites."""
    client = get_client(ctx)
    emit(ctx, sites_resources.list_sites(client, limit=limit, offset=offset))


@sites_app.command("get")
@appify
def get_site(
    ctx: typer.Context,
    site_id: int = typer.Argument(help="Site ID."),
) -> None:
    """Fetch a single site by ID."""
    client = get_client(ctx)
    emit(ctx, sites_resources.get_site(client, site_id))


@sites_app.command("create")
@appify
def create_site(
    ctx: typer.Context,
    field: list[str] = typer.Option(  # noqa: B008
        ..., "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Create a site. Required fields: hostname, root_page_id."""
    client = get_client(ctx)
    result = sites_resources.create_site(client, parsing.parse_fields(field))
    emit(ctx, result)


@sites_app.command("update")
@appify
def update_site(
    ctx: typer.Context,
    site_id: int = typer.Argument(help="Site ID."),
    field: list[str] = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update a site (PUT — all required fields needed)."""
    if not _require_yes(ctx, yes, f"update site {site_id}"):
        return
    client = get_client(ctx)
    emit(
        ctx,
        sites_resources.update_site(client, site_id, parsing.parse_fields(field or [])),
    )


@sites_app.command("delete")
@appify
def delete_site(
    ctx: typer.Context,
    site_id: int = typer.Argument(help="Site ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a site (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete site {site_id}"):
        return
    client = get_client(ctx)
    emit(ctx, sites_resources.delete_site(client, site_id))


app.add_typer(sites_app, name="sites")
