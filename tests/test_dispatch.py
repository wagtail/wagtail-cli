import sys

import pytest

from wagtail_cli.cli import main as main_mod
from wagtail_cli.cli.main import cli, resolve_delegate


class _FakeSubprocess:
    def __init__(self, log):
        self._log = log

    def call(self, cmd):
        self._log.append(list(cmd))
        return 0


def _run_cli(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["wt", *argv])
    # cli() delegates by raising SystemExit with the subprocess's exit code;
    # callers handle the SystemExit.
    cli()


def test_delegate_manage_py(tmp_path, monkeypatch):
    (tmp_path / "manage.py").write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(main_mod, "find_project_python", lambda: sys.executable)
    assert resolve_delegate(["shell"]) == [
        sys.executable,
        str(tmp_path / "manage.py"),
        "shell",
    ]


def test_delegate_manage_py_wins_over_env(tmp_path, monkeypatch):
    (tmp_path / "manage.py").write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "x.settings")
    monkeypatch.setattr(main_mod, "find_project_python", lambda: sys.executable)
    got = resolve_delegate(["makemigrations"])
    assert got == [sys.executable, str(tmp_path / "manage.py"), "makemigrations"]


def test_delegate_manage_py_uses_project_interpreter(tmp_path, monkeypatch):
    (tmp_path / "manage.py").write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    monkeypatch.setattr(main_mod, "find_project_python", lambda: "/opt/venv/bin/python")
    assert resolve_delegate(["shell"]) == [
        "/opt/venv/bin/python",
        str(tmp_path / "manage.py"),
        "shell",
    ]


def test_delegate_django_admin_via_project_python(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # empty dir: no manage.py
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "x.settings")
    monkeypatch.setattr(main_mod, "find_project_python", lambda: "/opt/venv/bin/python")
    assert resolve_delegate(["runserver"]) == [
        "/opt/venv/bin/python",
        "-m",
        "django",
        "runserver",
    ]


def test_delegate_django_admin_falls_back_to_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # empty dir: no manage.py
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    assert resolve_delegate(["runserver"]) is None
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "x.settings")
    monkeypatch.setattr(main_mod, "find_project_python", lambda: None)
    assert resolve_delegate(["runserver"]) == ["django-admin", "runserver"]


def test_cli_delegates_unknown_command(tmp_path, monkeypatch):
    (tmp_path / "manage.py").write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main_mod, "find_project_python", lambda: sys.executable)
    called = []
    monkeypatch.setattr(main_mod, "subprocess", _FakeSubprocess(called))
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "runserver")
    assert called == [[sys.executable, str(tmp_path / "manage.py"), "runserver"]]


def test_cli_delegates_with_hint_when_django_unavailable(tmp_path, monkeypatch, capsys):
    (tmp_path / "manage.py").write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(main_mod, "find_project_python", lambda: None)
    monkeypatch.setattr(main_mod, "is_django_available", lambda: False)
    called = []
    monkeypatch.setattr(main_mod, "subprocess", _FakeSubprocess(called))
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "runserver")
    assert called == [[sys.executable, str(tmp_path / "manage.py"), "runserver"]]
    err = capsys.readouterr().err
    assert "Django is not importable" in err
    assert "uv run --with wagtail-cli" in err


def test_cli_no_manage_py_no_settings_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # empty dir: no manage.py
    monkeypatch.delenv("DJANGO_SETTINGS_MODULE", raising=False)
    called = []
    monkeypatch.setattr(main_mod, "subprocess", _FakeSubprocess(called))
    with pytest.raises(SystemExit) as excinfo:
        _run_cli(monkeypatch, "runserver")
    assert excinfo.value.code == 1
    assert called == []


def test_cli_version_is_clean_zero_exit(monkeypatch, capsys):
    monkeypatch.setattr(main_mod, "_capture", lambda cmd: None)
    with pytest.raises(SystemExit) as excinfo:
        _run_cli(monkeypatch, "--version")
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert out.startswith("wagtail-cli ")
    assert "Traceback" not in out


def test_cli_version_appends_detected_versions(monkeypatch, capsys):
    monkeypatch.setattr(main_mod, "find_project_python", lambda: "/opt/venv/bin/python")
    versions = {"wagtail": "6.0", "django": "5.2"}
    monkeypatch.setattr(
        main_mod, "package_version", lambda python, package: versions.get(package)
    )
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "--version")
    out = capsys.readouterr().out
    assert "wagtail-cli " in out
    assert "Wagtail: 6.0" in out
    assert "Django: 5.2" in out


def test_cli_version_skips_versions_without_project_interpreter(monkeypatch, capsys):
    monkeypatch.setattr(main_mod, "find_project_python", lambda: None)
    with pytest.raises(SystemExit):
        _run_cli(monkeypatch, "--version")
    out = capsys.readouterr().out
    assert out.startswith("wagtail-cli ")
    assert "Wagtail:" not in out
    assert "Django:" not in out


def test_cli_help_is_clean_zero_exit(monkeypatch, capsys):
    monkeypatch.setattr(main_mod, "_capture", lambda cmd: None)
    with pytest.raises(SystemExit) as excinfo:
        _run_cli(monkeypatch, "--help")
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "Usage" in out  # typer help rendered
    assert "Traceback" not in out
