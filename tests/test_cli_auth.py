import respx

from typer.testing import CliRunner

from wgtl_api_cli.cli.main import app


BASE = "https://x.test/api/v3"
runner = CliRunner()


def _env(monkeypatch):
    monkeypatch.setenv("WAGTAIL_BASE_URL", BASE)
    monkeypatch.setenv("WAGTAIL_TOKEN", "tok")


@respx.mock
def test_whoami_json_when_piped(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/whoami/").respond(200, json={"user": {"username": "admin"}})
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 0
    assert '"username":"admin"' in result.output  # compact JSON (not a TTY)


@respx.mock
def test_whoami_auth_error_exit_4(monkeypatch):
    _env(monkeypatch)
    respx.get(f"{BASE}/whoami/").respond(
        401, json={"title": "Unauthorized", "status": 401}
    )
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 4
    assert "Unauthorized" in result.output


def test_whoami_unconfigured_exit_2(monkeypatch):
    monkeypatch.delenv("WAGTAIL_BASE_URL", raising=False)
    monkeypatch.delenv("WAGTAIL_TOKEN", raising=False)
    result = runner.invoke(app, ["--url", BASE, "whoami"])  # url but no token
    assert result.exit_code == 2
    assert "wgtl init" in result.output


def test_conflicting_output_flags_exit_2_no_traceback():
    result = runner.invoke(app, ["--json", "--human", "whoami"])
    assert result.exit_code == 2
    assert "Cannot combine --json and --human" in result.stderr
    assert "Traceback" not in result.output
    assert "Traceback" not in result.stderr


@respx.mock
def test_init_writes_dotfile(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "wgtl_api_cli.config._user_dotfile", lambda: tmp_path / ".wgtl.toml"
    )
    respx.get(f"{BASE}/whoami/").respond(200, json={"user": {"username": "admin"}})
    result = runner.invoke(app, ["--url", BASE, "--token", "tok123", "init"])
    assert result.exit_code == 0
    data = (tmp_path / ".wgtl.toml").read_text()
    assert 'url = "https://x.test/api/v3"' in data and 'token = "tok123"' in data
