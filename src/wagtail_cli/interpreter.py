"""Locate the Python interpreter of the surrounding Django project.

wagtail-cli is often installed in isolation (``uv tool install wagtail-cli``,
``pipx``), away from the Django project it operates on. Running the project's
``manage.py`` with the tool's own interpreter fails when Django is not
installed there. These helpers pick a more suitable interpreter: the current
one when Django is importable, otherwise a project virtualenv discovered via
``$VIRTUAL_ENV`` or conventional ``.venv`` / ``venv`` directories.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

from pathlib import Path


_VENV_DIR_NAMES = (".venv", "venv")


def is_django_available() -> bool:
    """Return True when Django is importable in the current interpreter."""
    return importlib.util.find_spec("django") is not None


def venv_python(venv_dir: Path) -> Path:
    """Return the interpreter path inside a virtualenv directory."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_candidates(cwd: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    env_venv = os.environ.get("VIRTUAL_ENV")
    if env_venv:
        candidates.append(Path(env_venv))
    root = Path.cwd() if cwd is None else cwd
    candidates.extend(root / name for name in _VENV_DIR_NAMES)
    return candidates


def find_project_python(cwd: Path | None = None) -> str | None:
    """Return a Python interpreter for running the project's Django code.

    Resolution order: the current interpreter when Django is importable
    there, then ``$VIRTUAL_ENV``, then ``.venv`` / ``venv`` directories in
    ``cwd``. Returns None when no candidate is found.
    """
    if is_django_available():
        return sys.executable
    for venv_dir in _venv_candidates(cwd):
        python = venv_python(venv_dir)
        if python.is_file():
            return str(python)
    return None


def package_version(python: str, package: str) -> str | None:
    """Return the installed version of ``package`` for a given interpreter."""
    code = f"import importlib.metadata as m; print(m.version({package!r}))"
    try:
        proc = subprocess.run(  # noqa: S603  # fixed interpreter + generated code, no shell
            [python, "-c", code],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None
