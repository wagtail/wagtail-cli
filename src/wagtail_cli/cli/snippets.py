from __future__ import annotations

import typer

from wagtail_cli import parsing
from wagtail_cli.resources import snippets as snippets_resources

from ._shared import require_yes as _require_yes
from .main import api_app, appify, emit, get_client


snippets_app = typer.Typer(
    name="snippets",
    help="Read, create, and manage API-ENABLED snippets (including actions and "
    "revisions).",
    no_args_is_help=True,
)


@snippets_app.command("list")
@appify
def list_snippets(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    locale: str | None = typer.Option(None, "--locale", help="Filter by locale code."),
    translation_of: str | None = typer.Option(
        None, "--translation-of", help="Translation of snippet ID."
    ),
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
    """List snippets of a type with optional filters, ordering, pagination."""
    client = get_client(ctx)
    result = snippets_resources.list_snippets(
        client,
        type,
        locale=locale,
        translation_of=translation_of,
        search=search,
        search_operator=search_operator,
        order=order,
        limit=limit,
        offset=offset,
    )
    emit(ctx, result)


@snippets_app.command("get")
@appify
def get_snippet(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
) -> None:
    """Fetch a single snippet by type and ID."""
    client = get_client(ctx)
    emit(ctx, snippets_resources.get_snippet(client, type, pk))


@snippets_app.command("create")
@appify
def create_snippet(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    field: list[str] = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
) -> None:
    """Create a snippet of the given type."""
    client = get_client(ctx)
    result = snippets_resources.create_snippet(
        client, type, parsing.parse_fields(field or [])
    )
    emit(ctx, result)


@snippets_app.command("update")
@appify
def update_snippet(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    field: list[str] = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update (PATCH) a snippet. Sends only provided fields."""
    if not _require_yes(ctx, yes, f"update snippet {type} {pk}"):
        return
    client = get_client(ctx)
    result = snippets_resources.update_snippet(
        client, type, pk, parsing.parse_fields(field or [])
    )
    emit(ctx, result)


@snippets_app.command("delete")
@appify
def delete_snippet(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a snippet (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete snippet {type} {pk}"):
        return
    client = get_client(ctx)
    emit(ctx, snippets_resources.delete_snippet(client, type, pk))


@snippets_app.command("publish")
@appify
def publish(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
) -> None:
    """Publish a snippet (only supported for publishing-enabled types)."""
    client = get_client(ctx)
    emit(ctx, snippets_resources.publish_snippet(client, type, pk))


@snippets_app.command("unpublish")
@appify
def unpublish(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
) -> None:
    """Unpublish a snippet (only supported for publishing-enabled types)."""
    client = get_client(ctx)
    emit(ctx, snippets_resources.unpublish_snippet(client, type, pk))


@snippets_app.command("revert")
@appify
def revert(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    revision: int = typer.Option(..., "--revision", help="Revision ID."),
) -> None:
    """Revert a snippet to a previous revision."""
    client = get_client(ctx)
    emit(
        ctx,
        snippets_resources.revert_snippet(client, type, pk, revision_id=revision),
    )


@snippets_app.command("copy-for-translation")
@appify
def copy_for_translation(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    locale: str = typer.Option(..., "--locale", help="Target locale code."),
) -> None:
    """Copy a snippet for translation into a locale."""
    client = get_client(ctx)
    emit(
        ctx,
        snippets_resources.copy_snippet_for_translation(
            client, type, pk, locale=locale
        ),
    )


revisions_app = typer.Typer(
    name="revisions", help="Snippet revisions.", no_args_is_help=True
)


@revisions_app.command("list")
@appify
def revisions_list(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    limit: int | None = typer.Option(None, "--limit", help="Max items."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List the revisions of a snippet."""
    client = get_client(ctx)
    emit(
        ctx,
        snippets_resources.list_snippet_revisions(
            client, type, pk, limit=limit, offset=offset
        ),
    )


@revisions_app.command("get")
@appify
def revisions_get(
    ctx: typer.Context,
    type: str = typer.Argument(help="Snippet type, e.g. base.FooterText."),
    pk: str = typer.Argument(help="Snippet ID."),
    revision_id: int = typer.Argument(help="Revision ID."),
) -> None:
    """Fetch a single revision of a snippet."""
    client = get_client(ctx)
    emit(ctx, snippets_resources.get_snippet_revision(client, type, pk, revision_id))


snippets_app.add_typer(revisions_app, name="revisions")
api_app.add_typer(snippets_app, name="snippets")
