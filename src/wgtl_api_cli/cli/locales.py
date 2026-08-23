from __future__ import annotations

import typer

from wgtl_api_cli import parsing
from wgtl_api_cli.resources import locales as locales_resources

from ._shared import require_yes as _require_yes
from .main import app, appify, emit, get_client


locales_app = typer.Typer(
    name="locales",
    help="List, view, create, and manage locales.",
    no_args_is_help=True,
)


@locales_app.command("list")
@appify
def list_locales(
    ctx: typer.Context,
    limit: int | None = typer.Option(None, "--limit", help="Maximum items per page."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List locales."""
    client = get_client(ctx)
    emit(
        ctx,
        locales_resources.list_locales(client, limit=limit, offset=offset),
    )


@locales_app.command("get")
@appify
def get_locale(
    ctx: typer.Context,
    locale_id: int = typer.Argument(help="Locale ID."),
) -> None:
    """Fetch a single locale by ID."""
    client = get_client(ctx)
    emit(ctx, locales_resources.get_locale(client, locale_id))


@locales_app.command("create")
@appify
def create_locale(
    ctx: typer.Context,
    field: list[str] = typer.Option(  # noqa: B008
        ..., "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Create a locale. Required field: language_code."""
    client = get_client(ctx)
    result = locales_resources.create_locale(client, parsing.parse_fields(field))
    emit(ctx, result)


@locales_app.command("update")
@appify
def update_locale(
    ctx: typer.Context,
    locale_id: int = typer.Argument(help="Locale ID."),
    field: list[str] = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update a locale (PUT — language_code required)."""
    if not _require_yes(ctx, yes, f"update locale {locale_id}"):
        return
    client = get_client(ctx)
    emit(
        ctx,
        locales_resources.update_locale(
            client, locale_id, parsing.parse_fields(field or [])
        ),
    )


@locales_app.command("delete")
@appify
def delete_locale(
    ctx: typer.Context,
    locale_id: int = typer.Argument(help="Locale ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a locale (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete locale {locale_id}"):
        return
    client = get_client(ctx)
    emit(ctx, locales_resources.delete_locale(client, locale_id))


app.add_typer(locales_app, name="locales")
