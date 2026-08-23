from __future__ import annotations

import sys

from typing import Any

import typer

from wgtl_api_cli import parsing
from wgtl_api_cli.errors import UsageError
from wgtl_api_cli.resources import pages as pages_resources

from .main import app, appify, emit, get_client


pages_app = typer.Typer(
    name="pages",
    help="Read, create, and manage pages (including actions and revisions).",
    no_args_is_help=True,
)


def _is_tty() -> bool:
    """Whether stdin is interactive (used before prompting for confirmation)."""
    return sys.stdin.isatty()


def _resolve_ref(ctx: typer.Context, raw: str) -> Any:
    """Resolve a page REF (numeric id or URL path) to a numeric page id.

    In dry-run mode we cannot probe the server, so a path REF passes through
    unresolved (the preview still shows what would be sent).
    """
    if raw.isdigit():
        return int(raw)
    if ctx.obj.dry_run:
        return raw
    return parsing.resolve_page_ref(get_client(ctx), raw)


def _require_yes(ctx: typer.Context, yes: bool, what: str) -> bool:
    """Return True if the operation should proceed.

    With --yes always proceed; on a TTY prompt for confirmation; on a
    non-TTY refuse with a usage error (scripts must pass --yes).
    """
    if yes:
        return True
    if not _is_tty():
        raise UsageError(
            f"Refusing to {what} on a non-interactive terminal; pass --yes."
        )
    return typer.confirm(f"{what.capitalize()}? Are you sure?")


@pages_app.command("list")
@appify
def list_pages(
    ctx: typer.Context,
    type: list[str] | None = typer.Option(  # noqa: B008
        None, "--type", help="Filter by page type (repeatable)."
    ),
    child_of: str | None = typer.Option(
        None, "--child-of", help="Direct child of REF."
    ),
    descendant_of: str | None = typer.Option(
        None, "--descendant-of", help="Descendant of REF."
    ),
    ancestor_of: str | None = typer.Option(
        None, "--ancestor-of", help="Ancestor of REF."
    ),
    translation_of: str | None = typer.Option(
        None, "--translation-of", help="Translation of page ID."
    ),
    locale: str | None = typer.Option(None, "--locale", help="Filter by locale code."),
    site: str | None = typer.Option(None, "--site", help="Filter by site."),
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
    """List pages with optional filters, ordering, and pagination."""
    client = get_client(ctx)
    result = pages_resources.list_pages(
        client,
        type=type,
        child_of=child_of,
        descendant_of=descendant_of,
        ancestor_of=ancestor_of,
        translation_of=translation_of,
        locale=locale,
        site=site,
        search=search,
        search_operator=search_operator,
        order=order,
        limit=limit,
        offset=offset,
    )
    emit(ctx, result)


@pages_app.command("find")
@appify
def find_page(
    ctx: typer.Context,
    id: str | None = typer.Option(None, "--id", help="Find by page ID."),
    path: str | None = typer.Option(None, "--path", help="Find by URL path."),
    site: str | None = typer.Option(None, "--site", help="Find within a site."),
) -> None:
    """Locate a page by ID or URL path, returning its API location."""
    if id is None and path is None:
        raise UsageError("Provide one of --id or --path to find a page.")
    client = get_client(ctx)
    result = pages_resources.find_page(client, id=id, html_path=path, site=site)
    emit(ctx, result)


@pages_app.command("get")
@appify
def get_page(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    version: str | None = typer.Option(
        None, "--version", help="'draft' (default) or 'live'."
    ),
    html: bool = typer.Option(False, "--html", help="Return rich text fields as HTML."),
) -> None:
    """Fetch a single page by ID."""
    client = get_client(ctx)
    rich_text_format = "html" if html else None
    result = pages_resources.get_page(
        client, page_id, version=version, rich_text_format=rich_text_format
    )
    emit(ctx, result)


@pages_app.command("create")
@appify
def create_page(
    ctx: typer.Context,
    type_name: str = typer.Argument(help="Page type, e.g. blog.BlogPage."),
    parent: str = typer.Option(..., "--parent", help="Parent page REF."),
    title: str = typer.Option(..., "--title", help="Page title."),
    slug: str | None = typer.Option(None, "--slug", help="URL slug."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    publish: bool = typer.Option(False, "--publish", help="Publish the new page."),
) -> None:
    """Create a page as a draft (or publish it with --publish)."""
    client = get_client(ctx)
    parent_id = _resolve_ref(ctx, parent)
    payload = pages_resources.build_page_payload(
        type_name=type_name,
        parent_id=parent_id,
        title=title,
        slug=slug,
        fields=parsing.parse_fields(field or []),
        publish=publish,
    )
    result = pages_resources.create_page(client, payload)
    emit(ctx, result)


@pages_app.command("update")
@appify
def update_page(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    title: str | None = typer.Option(None, "--title", help="New page title."),
    slug: str | None = typer.Option(None, "--slug", help="New URL slug."),
    field: list[str] | None = typer.Option(  # noqa: B008
        None, "--field", help="Set a field KEY:VALUE (repeatable)."
    ),
    publish: bool = typer.Option(False, "--publish", help="Publish after updating."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Update (PATCH) a page. Sends only provided fields by default."""
    if not _require_yes(ctx, yes, f"update page {page_id}"):
        return
    client = get_client(ctx)
    payload = pages_resources.build_page_payload(
        title=title,
        slug=slug,
        fields=parsing.parse_fields(field or []),
        for_create=False,
    )
    result = pages_resources.update_page(client, page_id, payload)
    if publish:
        result = pages_resources.publish_page(client, page_id)
    emit(ctx, result)


@pages_app.command("delete")
@appify
def delete_page(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation."),
) -> None:
    """Delete a page (confirmation required unless --yes)."""
    if not _require_yes(ctx, yes, f"delete page {page_id}"):
        return
    client = get_client(ctx)
    result = pages_resources.delete_page(client, page_id)
    emit(ctx, result)


@pages_app.command("publish")
@appify
def publish(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
) -> None:
    """Publish a page's latest revision."""
    client = get_client(ctx)
    emit(ctx, pages_resources.publish_page(client, page_id))


@pages_app.command("unpublish")
@appify
def unpublish(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
) -> None:
    """Unpublish a page, moving it back to draft."""
    client = get_client(ctx)
    emit(ctx, pages_resources.unpublish_page(client, page_id))


@pages_app.command("copy")
@appify
def copy(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID to copy."),
    destination: str = typer.Option(
        ..., "--destination", help="Destination parent REF."
    ),
    slug: str | None = typer.Option(None, "--slug", help="New slug."),
    title: str | None = typer.Option(None, "--title", help="New title."),
    recursive: bool = typer.Option(
        None,
        "--recursive/--no-recursive",
        help="Copy descendants.",
    ),
    keep_live: bool = typer.Option(
        None,
        "--keep-live/--no-keep-live",
        help="Keep copied pages live.",
    ),
) -> None:
    """Copy a page to a new location."""
    client = get_client(ctx)
    destination_id = _resolve_ref(ctx, destination)
    result = pages_resources.copy_page(
        client,
        page_id,
        destination_id=destination_id,
        slug=slug,
        title=title,
        recursive=recursive,
        keep_live=keep_live,
    )
    emit(ctx, result)


@pages_app.command("move")
@appify
def move(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID to move."),
    destination: str = typer.Option(
        ..., "--destination", help="Destination parent REF."
    ),
) -> None:
    """Move a page to a new parent."""
    client = get_client(ctx)
    destination_id = _resolve_ref(ctx, destination)
    emit(
        ctx,
        pages_resources.move_page(client, page_id, destination_id=destination_id),
    )


@pages_app.command("revert")
@appify
def revert(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    revision: int = typer.Option(..., "--revision", help="Revision ID."),
) -> None:
    """Revert a page to a previous revision."""
    client = get_client(ctx)
    emit(
        ctx,
        pages_resources.revert_page(client, page_id, revision_id=revision),
    )


@pages_app.command("create-alias")
@appify
def create_alias(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID to alias."),
    destination: str = typer.Option(
        ..., "--destination", help="Destination parent REF."
    ),
) -> None:
    """Create an alias of a page."""
    client = get_client(ctx)
    destination_id = _resolve_ref(ctx, destination)
    emit(
        ctx,
        pages_resources.create_alias(client, page_id, destination_id=destination_id),
    )


@pages_app.command("convert-alias")
@appify
def convert_alias(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Alias page ID."),
) -> None:
    """Convert an alias into an ordinary page."""
    client = get_client(ctx)
    emit(ctx, pages_resources.convert_alias(client, page_id))


@pages_app.command("copy-for-translation")
@appify
def copy_for_translation(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    locale: str = typer.Option(..., "--locale", help="Target locale code."),
) -> None:
    """Copy a page for translation into a locale."""
    client = get_client(ctx)
    emit(ctx, pages_resources.copy_for_translation(client, page_id, locale=locale))


revisions_app = typer.Typer(
    name="revisions", help="Page revisions.", no_args_is_help=True
)


@revisions_app.command("list")
@appify
def revisions_list(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    limit: int | None = typer.Option(None, "--limit", help="Max items."),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset."),
) -> None:
    """List the revisions of a page."""
    client = get_client(ctx)
    emit(
        ctx,
        pages_resources.list_revisions(client, page_id, limit=limit, offset=offset),
    )


@revisions_app.command("get")
@appify
def revisions_get(
    ctx: typer.Context,
    page_id: int = typer.Argument(help="Page ID."),
    revision_id: int = typer.Argument(help="Revision ID."),
) -> None:
    """Fetch a single revision of a page."""
    client = get_client(ctx)
    emit(ctx, pages_resources.get_revision(client, page_id, revision_id))


pages_app.add_typer(revisions_app, name="revisions")
app.add_typer(pages_app, name="pages")
