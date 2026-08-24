from __future__ import annotations

from typing import Any

import typer

from wagtail_cli import output
from wagtail_cli.resources import schema as schema_resources

from .main import api_app, appify, emit, get_client


schema_app = typer.Typer(
    name="schema",
    help="Discover the content model and inspect per-type schemas.",
    no_args_is_help=True,
)


@schema_app.command("list")
@appify
def list_types(ctx: typer.Context) -> None:
    """List registered content types."""
    client = get_client(ctx)
    emit(ctx, schema_resources.list_types(client))


@schema_app.command("show")
@appify
def show_type(
    ctx: typer.Context,
    type_name: str = typer.Argument(help="Content type, e.g. blog.BlogPage."),
) -> None:
    """Print the raw read/create/patch schema for a content type as JSON."""
    client = get_client(ctx)
    data: Any = schema_resources.get_type_schema(client, type_name)
    # Always JSON — these schemas are the machine-readable contract and are
    # not suited to the human table rendering.
    typer.echo(output.render(data, "json"))


api_app.add_typer(schema_app, name="schema")
