from __future__ import annotations

from pathlib import Path

import typer

from wagtail_cli import parsing
from wagtail_cli.errors import UsageError
from wagtail_cli.resources import images as images_resources

from ._shared import is_tty as _is_tty  # noqa: F401
from ._shared import require_yes as _require_yes
from .main import app, appify, emit, get_client


images_app = typer.Typer(
    name="images",
    help="List, view, upload, and manage images.",
    no_args_is_help=True,
)


@images_app.command("list")
@appify
def list_images(
    ctx: typer.Context,
    search: str | None = typer.Option(None, "--search", help="Full-text search query."),
    search_operator: str | None = typer.Option(
        None, "--search-operator", help="'and' or 'or' search operation."
    ),
    order: str | None = typer.Option(
        None, "--order", help="Sort field (prefix - to reverse)."
    ),
    limit: int | None = typer.Option(None, "--limit", help="Maximum items per page."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List images with optional filters, ordering, and pagination."""
    client = get_client(ctx)
    emit(
        ctx,
        images_resources.list_images(
            client,
            search=search,
            search_operator=search_operator,
            order=order,
            limit=limit,
            offset=offset,
        ),
    )


@images_app.command("get")
@appify
def get_image(
    ctx: typer.Context,
    image_id: int = typer.Argument(help="Image ID."),
) -> None:
    """Fetch a single image by ID."""
    client = get_client(ctx)
    emit(ctx, images_resources.get_image(client, image_id))


@images_app.command("create")
@appify
def create_image(
    ctx: typer.Context,
    file: Path = typer.Argument(  # noqa: B008
        help="Path to the image file to upload."
    ),
    title: str = typer.Option(..., "--title", help="Image title."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set an extra form field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Upload an image (multipart/form-data)."""
    if not file.is_file():
        raise UsageError(f"Cannot read file: {file}")
    client = get_client(ctx)
    result = images_resources.create_image(
        client,
        file=file,
        title=title,
        fields=parsing.parse_fields(field or []),
    )
    emit(ctx, result)


@images_app.command("update")
@appify
def update_image(
    ctx: typer.Context,
    image_id: int = typer.Argument(help="Image ID."),
    title: str | None = typer.Option(None, "--title", help="New image title."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update (PATCH) an image's metadata. Sends only provided fields."""
    if not _require_yes(ctx, yes, f"update image {image_id}"):
        return
    body: dict = {}
    if title:
        body["title"] = title
    body.update(parsing.parse_fields(field or []))
    client = get_client(ctx)
    emit(ctx, images_resources.update_image(client, image_id, body))


@images_app.command("delete")
@appify
def delete_image(
    ctx: typer.Context,
    image_id: int = typer.Argument(help="Image ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete an image (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete image {image_id}"):
        return
    client = get_client(ctx)
    emit(ctx, images_resources.delete_image(client, image_id))


app.add_typer(images_app, name="images")
