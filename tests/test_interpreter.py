"""Tests for project interpreter resolution."""

import os
import sys

from pathlib import Path

from wagtail_cli import interpreter


def test_find_project_python_prefers_current_interpreter(monkeypatch, tmp_path):
    monkeypatch.setattr(interpreter, "is_django_available", lambda: True)
    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "env-venv"))
    assert interpreter.find_project_python(cwd=tmp_path) == sys.executable


def test_find_project_python_uses_virtual_env(monkeypatch, tmp_path):
    monkeypatch.setattr(interpreter, "is_django_available", lambda: False)
    python = interpreter.venv_python(tmp_path / "env-venv")
    python.parent.mkdir(parents=True)
    python.write_text("")
    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "env-venv"))
    assert interpreter.find_project_python(cwd=tmp_path) == str(python)


def test_find_project_python_prefers_virtual_env_over_local_dirs(monkeypatch, tmp_path):
    monkeypatch.setattr(interpreter, "is_django_available", lambda: False)
    env_venv = tmp_path / "env-venv"
    env_python = interpreter.venv_python(env_venv)
    env_python.parent.mkdir(parents=True)
    env_python.write_text("")
    dot_venv = interpreter.venv_python(tmp_path / ".venv")
    dot_venv.parent.mkdir(parents=True)
    dot_venv.write_text("")
    monkeypatch.setenv("VIRTUAL_ENV", str(env_venv))
    assert interpreter.find_project_python(cwd=tmp_path) == str(env_python)


def test_find_project_python_discovers_venv_dirs(monkeypatch, tmp_path):
    monkeypatch.setattr(interpreter, "is_django_available", lambda: False)
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    dot_venv = interpreter.venv_python(tmp_path / ".venv")
    dot_venv.parent.mkdir(parents=True)
    dot_venv.write_text("")
    assert interpreter.find_project_python(cwd=tmp_path) == str(dot_venv)


def test_find_project_python_ignores_missing_venv_interpreters(monkeypatch, tmp_path):
    monkeypatch.setattr(interpreter, "is_django_available", lambda: False)
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    (tmp_path / ".venv" / "bin").mkdir(parents=True)  # empty bin dir
    assert interpreter.find_project_python(cwd=tmp_path) is None


def test_venv_python_windows_layout(monkeypatch, tmp_path):
    monkeypatch.setattr(os, "name", "nt")
    assert interpreter.venv_python(tmp_path) == tmp_path / "Scripts" / "python.exe"


def test_package_version_reports_installed_package():
    version = interpreter.package_version(sys.executable, "pytest")
    assert version is not None
    assert version[0].isdigit()


def test_package_version_returns_none_for_missing_package():
    assert interpreter.package_version(sys.executable, "not-a-real-package") is None


def test_package_version_returns_none_for_missing_interpreter():
    missing = str(Path("definitely") / "missing" / "python")
    assert interpreter.package_version(missing, "pytest") is None
