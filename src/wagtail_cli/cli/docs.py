"""`wt docs`: read docs.wagtail.org from the terminal."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import typer

from wagtail_cli import __version__, docs
from wagtail_cli.errors import NetworkError, NotFoundError, UsageError, WgtlError

from .main import appify


class DocsGroup(typer.core.TyperGroup):
    """Route unknown subcommands to the hidden `path` command.

    Lets `wt docs releases/8.0` work alongside `wt docs api` and
    `wt docs search`, mirroring the Stripe CLI docs viewer.
    """

    def resolve_command(self, ctx, args):
        if args and args[0] not in self.commands:
            args = ["path", *args]
        return super().resolve_command(ctx, args)


@dataclass
class DocsContext:
    docs_url: str
    language: str
    version: str


docs_app = typer.Typer(
    name="docs",
    help=(
        "Read Wagtail documentation (docs.wagtail.org) as Markdown. "
        "Run `wt docs releases/8.0` to fetch a page, `wt docs api` for the "
        "v3 API reference, and `wt docs search picture` to search."
    ),
    cls=DocsGroup,
    invoke_without_command=True,
    no_args_is_help=False,
)


from .main import app  # noqa: E402  # attach the docs group to the root app


app.add_typer(docs_app, name="docs")


def _docs_context(ctx: typer.Context) -> DocsContext:
    cc: DocsContext = ctx.obj
    return cc


def _get(url: str, params: dict | None = None) -> httpx.Response:
    try:
        return httpx.get(
            url,
            params=params,
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": f"wagtail-cli/{__version__}"},
        )
    except httpx.HTTPError as e:
        raise NetworkError(f"Could not reach {url}: {e}") from e


def _fetch_markdown(url: str) -> str:
    response = _get(url)
    if response.status_code == 404:
        raise NotFoundError(f"Page not found: {url}", status_code=404)
    if response.status_code != 200:
        raise WgtlError(
            f"Unexpected response fetching {url}: HTTP {response.status_code}",
            status_code=response.status_code,
        )
    # Missing versioned pages redirect to an HTML index (HTTP 200), so treat
    # a 200 response that is not Markdown as a missing page.
    if not _is_markdown(response):
        raise NotFoundError(f"Page not found: {url}", status_code=404)
    return response.text


def _is_markdown(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "")
    return content_type.startswith(("text/markdown", "text/plain"))


def _fetch_page_markdown(
    cc: DocsContext,
    path: str,
) -> str:
    """Fetch a docs page, falling back to stable when a versioned page 404s."""
    url = docs.resolve_page_url(cc.docs_url, cc.language, cc.version, path)
    stable_url = docs.resolve_page_url(cc.docs_url, cc.language, "stable", path)
    try:
        return _fetch_markdown(url)
    except NotFoundError:
        if url == stable_url:
            raise
        pass
    try:
        content = _fetch_markdown(stable_url)
    except NotFoundError:
        raise NotFoundError(
            f"Page not found: {url} (also checked {stable_url}). "
            "The page may not exist in this version of the docs.",
            status_code=404,
        ) from None
    typer.echo(f"Note: found in stable instead of {cc.version}.", err=True)
    return content


def _show_docs_page(ctx: typer.Context, path: str | None) -> None:
    cc = _docs_context(ctx)
    resolved_path = path if path else ""
    content = _fetch_page_markdown(cc, resolved_path)
    if not path:
        try:
            content = docs.extract_index_section(content)
        except ValueError as e:
            raise UsageError(str(e)) from e
    typer.echo(content)


@docs_app.callback(invoke_without_command=True)
@appify
def docs_callback(
    ctx: typer.Context,
    docs_url: str | None = typer.Option(
        None,
        "--docs-url",
        help=(
            "Docs site base URL (defaults to WAGTAIL_CLI_DOCS_URL or "
            "https://docs.wagtail.org)."
        ),
    ),
    language: str = typer.Option(
        docs.DEFAULT_LANGUAGE,
        "--language",
        help="Docs language, e.g. en (only en is published today).",
    ),
    version: str | None = typer.Option(
        None,
        "--version",
        help=(
            "Docs version (stable, latest, or e.g. 7.2). Defaults to the "
            "locally installed Wagtail version, then stable."
        ),
    ),
) -> None:
    """Read Wagtail documentation. `wt docs [PATH]` prints a page as Markdown."""
    ctx.obj = DocsContext(
        docs_url=docs.resolve_docs_url(docs_url),
        language=language,
        version=docs.resolve_version(version),
    )
    if ctx.invoked_subcommand is None:
        _show_docs_page(ctx, None)


@docs_app.command(name="path", hidden=True)
@appify
def docs_path(
    ctx: typer.Context,
    path: list[str] = typer.Argument(  # noqa: B008
        None, help="Docs path or URL."
    ),
) -> None:
    """Fetch a docs page by path or URL (hidden alias for `wt docs [PATH]`)."""
    _show_docs_page(ctx, "/".join(path or []))


@docs_app.command()
@appify
def api(
    ctx: typer.Context,
    operation: list[str] = typer.Argument(None),  # noqa: B008
) -> None:
    """Look up v3 API reference docs. With no argument, list all operations."""
    cc = _docs_context(ctx)
    markdown = _fetch_page_markdown(cc, docs.REFERENCE_PATH)

    operations = docs.parse_operations(markdown)
    if not operation:
        typer.echo(
            "The v3 API reference below covers Wagtail's built-in API. "
            "Operations added by your project are not included.\n"
        )
        for op in operations:
            typer.echo(op.heading)
        return

    exact, similar = docs.find_operations(operations, " ".join(operation))
    if len(exact) == 1:
        op = exact[0]
        typer.echo(f"### {op.heading}\n\n{op.body}")
        return
    if len(exact) > 1:
        raise UsageError(
            f"Ambiguous operation {' '.join(operation)!r}. "
            "Add the HTTP method to disambiguate:\n"
            + "\n".join(f"  {op.heading}" for op in exact)
        )
    if similar:
        raise UsageError(
            f"No operation matches {' '.join(operation)!r}. Closest matches:\n"
            + "\n".join(f"  {op.heading}" for op in similar)
        )
    raise UsageError(
        f"No operation matches {' '.join(operation)!r} in Wagtail's built-in "
        "v3 API. Operations may be project-specific: API-enabled apps add "
        "endpoints not listed in the shared reference. Run `wt docs api` to "
        "view the index of built-in operations."
    )


@docs_app.command()
@appify
def search(
    ctx: typer.Context,
    query: list[str] = typer.Argument(..., help="Search terms."),  # noqa: B008
    json_output: bool = typer.Option(
        False, "--json", help="Print the raw search API response as JSON."
    ),
) -> None:
    """Search the Wagtail docs via the site's search engine."""
    cc = _docs_context(ctx)
    url = f"{cc.docs_url}/{docs.SEARCH_PATH}"
    params = {"q": f"project:wagtail/{cc.version} {' '.join(query)}"}
    response = _get(url, params)
    if response.status_code != 200:
        raise WgtlError(
            f"Search failed: HTTP {response.status_code}",
            status_code=response.status_code,
        )
    payload: dict
    try:
        payload = response.json()
    except ValueError as e:
        raise WgtlError(f"Search returned a non-JSON response from {url}") from e
    if json_output:
        typer.echo(docs.search_payload_to_json(payload))
        return
    typer.echo(docs.format_search_results(payload))
    if not payload.get("results") and cc.version != "stable":
        typer.echo(
            f"Note: searched Wagtail {cc.version}. "
            "Try `wt docs --version stable search …` for all versions.",
            err=True,
        )
