from __future__ import annotations

import sys

import typer

from wagtail_cli.errors import UsageError

from .main import CliContext


def is_tty() -> bool:
    """Whether stdin is interactive (used before prompting for confirmation)."""
    return sys.stdin.isatty()


def _cli_context(ctx: typer.Context) -> CliContext:
    cc = ctx.find_object(CliContext)
    if cc is None:  # pragma: no cover - every command runs below the root app
        raise RuntimeError("CliContext not found in the Click context chain")
    return cc


SELECT_HELP = (
    "Return only these response fields (comma-separated or repeatable; "
    "supports dot paths). Equivalent to the global `wt --select`."
)

# Module-level singletons so command signatures can use them as defaults
# without triggering flake8-bugbear B008 (typer.Option() is a call). Their
# callbacks record the flag on the shared CliContext so any command that
# accepts them behaves exactly like the corresponding global option.
SELECT_OPTION = typer.Option(
    None,
    "--select",
    help=SELECT_HELP,
)


def _local_json_callback(ctx: typer.Context, param: typer.CallbackParam, value: bool):
    """Record a command-local --json flag on the shared CLI context."""
    if value:
        cc = _cli_context(ctx)
        if cc.local_fmt == "human":
            raise typer.BadParameter(
                "Cannot combine --json and --human", param_hint="--json/--human"
            )
        cc.local_fmt = "json"
    return value


def _local_human_callback(ctx: typer.Context, param: typer.CallbackParam, value: bool):
    """Record a command-local --human flag on the shared CLI context."""
    if value:
        cc = _cli_context(ctx)
        if cc.local_fmt == "json":
            raise typer.BadParameter(
                "Cannot combine --json and --human", param_hint="--json/--human"
            )
        cc.local_fmt = "human"
    return value


def _local_dry_run_callback(
    ctx: typer.Context, param: typer.CallbackParam, value: bool
):
    """Record a command-local --dry-run flag on the shared CLI context."""
    if value:
        _cli_context(ctx).local_dry_run = True
    return value


LOCAL_JSON_OPTION = typer.Option(
    False,
    "--json",
    callback=_local_json_callback,
    help="Force JSON output (same as the global --json).",
)
LOCAL_HUMAN_OPTION = typer.Option(
    False,
    "--human",
    callback=_local_human_callback,
    help="Force human-readable output (same as the global --human).",
)
LOCAL_DRY_RUN_OPTION = typer.Option(
    False,
    "--dry-run",
    callback=_local_dry_run_callback,
    help=(
        "Print the HTTP request that would be sent without sending it "
        "(same as the global --dry-run)."
    ),
)


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
