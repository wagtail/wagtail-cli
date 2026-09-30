from __future__ import annotations

from typing import Any

import typer

from wagtail_cli import output
from wagtail_cli.resources import schema as schema_resources

from ._shared import LOCAL_DRY_RUN_OPTION as _LOCAL_DRY_RUN_OPTION
from ._shared import LOCAL_HUMAN_OPTION as _LOCAL_HUMAN_OPTION
from ._shared import LOCAL_JSON_OPTION as _LOCAL_JSON_OPTION
from ._shared import SELECT_OPTION as _SELECT_OPTION
from .main import (
    api_app,
    appify,
    emit,
    get_client,
    resolve_output_format,
    resolve_select,
)


schema_app = typer.Typer(
    name="schema",
    help="Discover the content model and inspect per-type schemas.",
    no_args_is_help=True,
)


@schema_app.command("list")
@appify
def list_types(
    ctx: typer.Context,
    select: list[str] | None = _SELECT_OPTION,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
    dry_run: bool = _LOCAL_DRY_RUN_OPTION,
) -> None:
    """List registered content types."""
    client = get_client(ctx)
    emit(ctx, schema_resources.list_types(client), select=select)


@schema_app.command("show")
@appify
def show_type(
    ctx: typer.Context,
    type_name: str = typer.Argument(help="Content type, e.g. blog.BlogPage."),
    select: list[str] | None = _SELECT_OPTION,
    json: bool = _LOCAL_JSON_OPTION,
    human: bool = _LOCAL_HUMAN_OPTION,
    dry_run: bool = _LOCAL_DRY_RUN_OPTION,
) -> None:
    """Print the raw read/create/patch schema for a content type.

    JSON by default — these schemas are the machine-readable contract. Pass
    ``--human`` to render them with the human-readable formatter instead.
    """
    client = get_client(ctx)
    data: Any = schema_resources.get_type_schema(client, type_name)
    fmt = resolve_output_format(ctx) or "json"
    typer.echo(output.render(data, fmt, select=resolve_select(ctx, select)))


api_app.add_typer(schema_app, name="schema")
