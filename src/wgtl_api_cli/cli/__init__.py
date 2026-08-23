from __future__ import annotations

# Importing the command modules registers their Typer commands onto the root
# `app`. `main` is imported first to define the app before command groups
# attach to it.
from . import auth, documents, images, locales, main, pages, redirects, sites  # noqa: F401
