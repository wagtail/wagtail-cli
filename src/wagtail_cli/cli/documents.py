from __future__ import annotations

from pathlib import Path

import typer

from wagtail_cli import parsing
from wagtail_cli.errors import UsageError
from wagtail_cli.resources import documents as documents_resources

from ._shared import is_tty as _is_tty  # noqa: F401
from ._shared import require_yes as _require_yes
from .main import app, appify, emit, get_client


documents_app = typer.Typer(
    name="documents",
    help="List, view, upload, and manage documents.",
    no_args_is_help=True,
)


@documents_app.command("list")
@appify
def list_documents(
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
    """List documents with optional filters, ordering, and pagination."""
    client = get_client(ctx)
    emit(
        ctx,
        documents_resources.list_documents(
            client,
            search=search,
            search_operator=search_operator,
            order=order,
            limit=limit,
            offset=offset,
        ),
    )


@documents_app.command("get")
@appify
def get_document(
    ctx: typer.Context,
    document_id: int = typer.Argument(help="Document ID."),
) -> None:
    """Fetch a single document by ID."""
    client = get_client(ctx)
    emit(ctx, documents_resources.get_document(client, document_id))


@documents_app.command("create")
@appify
def create_document(
    ctx: typer.Context,
    file: Path = typer.Argument(  # noqa: B008
        help="Path to the document file to upload."
    ),
    title: str = typer.Option(..., "--title", help="Document title."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set an extra form field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Upload a document (multipart/form-data)."""
    if not file.is_file():
        raise UsageError(f"Cannot read file: {file}")
    client = get_client(ctx)
    result = documents_resources.create_document(
        client,
        file=file,
        title=title,
        fields=parsing.parse_fields(field or []),
    )
    emit(ctx, result)


@documents_app.command("update")
@appify
def update_document(
    ctx: typer.Context,
    document_id: int = typer.Argument(help="Document ID."),
    title: str | None = typer.Option(None, "--title", help="New document title."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update (PATCH) a document's metadata. Sends only provided fields."""
    if not _require_yes(ctx, yes, f"update document {document_id}"):
        return
    body: dict = {}
    if title:
        body["title"] = title
    body.update(parsing.parse_fields(field or []))
    client = get_client(ctx)
    emit(ctx, documents_resources.update_document(client, document_id, body))


@documents_app.command("delete")
@appify
def delete_document(
    ctx: typer.Context,
    document_id: int = typer.Argument(help="Document ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a document (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete document {document_id}"):
        return
    client = get_client(ctx)
    emit(ctx, documents_resources.delete_document(client, document_id))


app.add_typer(documents_app, name="documents")
