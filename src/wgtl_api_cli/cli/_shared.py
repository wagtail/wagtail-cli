from __future__ import annotations

import sys

import typer

from wgtl_api_cli.errors import UsageError


def is_tty() -> bool:
    """Whether stdin is interactive (used before prompting for confirmation)."""
    return sys.stdin.isatty()


def require_yes(ctx: typer.Context, yes: bool, what: str) -> bool:
    """Return True if the operation should proceed.

    With --yes always proceed; on a TTY prompt for confirmation; on a
    non-TTY refuse with a usage error (scripts must pass --yes).
    """
    if yes:
        return True
    if not is_tty():
        raise UsageError(
            f"Refusing to {what} on a non-interactive terminal; pass --yes."
        )
    return typer.confirm(f"{what.capitalize()}? Are you sure?")
