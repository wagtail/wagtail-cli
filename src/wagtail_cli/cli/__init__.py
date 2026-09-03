from __future__ import annotations

# Importing the command modules registers their Typer commands onto the
# `api_app` group. `main` is imported first to define the app and api_app
# before command groups attach to them.
from . import (  # noqa: F401
    auth,
    docs,
    documents,
    images,
    locales,
    main,
    pages,
    redirects,
    schema,
    sites,
    snippets,
)
